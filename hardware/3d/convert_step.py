# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MACRO12 contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# STEP model content is separately copyright Adafruit Industries and distributed
# under its MIT license; retain the accompanying original license notice.
"""Convert an official STEP assembly into named/color-grouped JSON meshes in mm.
Independent conversion using Open CASCADE XCAF, retaining occurrence placement.
"""
import argparse, json, hashlib
from pathlib import Path
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_Label
try:
    from OCP.collections import Sequence_TDF_Label as TDF_LabelSequence
except ImportError:
    from OCP.TDF import TDF_LabelSequence
from OCP.TDataStd import TDataStd_Name
from OCP.TDocStd import TDocStd_Document
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorSurf, XCAFDoc_ColorGen
from OCP.Quantity import Quantity_ColorRGBA
from OCP.TopLoc import TopLoc_Location
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.Interface import Interface_Static


def get_name(label):
    attr = TDataStd_Name()
    if label.IsAttribute(TDataStd_Name.GetID_s()):
        label.FindAttribute(TDataStd_Name.GetID_s(), attr)
        return attr.Get().ToExtString()
    return ''


def convert(input_path, output_path):
    reader = STEPCAFControl_Reader()
    reader.SetColorMode(True)
    reader.SetNameMode(True)
    reader.SetLayerMode(True)
    Interface_Static.SetIVal_s('read.stepcaf.subshapes.name', 1)
    Interface_Static.SetCVal_s('xstep.cascade.unit', 'MM')
    if reader.ReadFile(str(input_path)) != IFSelect_RetDone:
        raise RuntimeError('Cannot read STEP')
    doc = TDocStd_Document(TCollection_ExtendedString('MDTV-XCAF'))
    reader.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    parts=[]
    components=[]

    def color_of(item):
        col=Quantity_ColorRGBA()
        for kind in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen):
            try:
                found=ct.GetColor(item, kind, col)
            except TypeError:
                found=ct.GetColor_s(item,kind,col)
            if found:
                rgb=col.GetRGB()
                return [round(rgb.Red(),6),round(rgb.Green(),6),round(rgb.Blue(),6),round(col.Alpha(),6)]
        return None

    def emit_shape(label, loc, path, inherited):
        shape=st.GetShape_s(label)
        if shape.IsNull(): return
        base_color = color_of(label) or color_of(shape) or inherited or [0.55,0.55,0.55,1]
        mesher=BRepMesh_IncrementalMesh(shape,0.05,False,0.3,True)
        mesher.Perform()
        by_color={}
        explorer=TopExp_Explorer(shape,TopAbs_FACE)
        while explorer.More():
            cast_face = getattr(TopoDS, 'Face_s', None) or TopoDS.Face
            face=cast_face(explorer.Current())
            face_loc=TopLoc_Location()
            triangulation=BRep_Tool.Triangulation_s(face,face_loc)
            if triangulation is not None:
                color=color_of(face) or base_color
                group=by_color.setdefault(tuple(color),{'vertices':[],'faces':[]})
                offset=len(group['vertices'])
                transform=loc.Multiplied(face_loc).Transformation()
                for n in range(1,triangulation.NbNodes()+1):
                    point=triangulation.Node(n).Transformed(transform)
                    group['vertices'].append([round(point.X(),6),round(point.Y(),6),round(point.Z(),6)])
                for n in range(1,triangulation.NbTriangles()+1):
                    a,b,c=triangulation.Triangle(n).Get()
                    if face.Orientation()==TopAbs_REVERSED: b,c=c,b
                    group['faces'].append([offset+a-1,offset+b-1,offset+c-1])
            explorer.Next()
        all_vertices=[]
        component_id=len(components)
        for gi,(color,geometry) in enumerate(by_color.items()):
            vs=geometry['vertices']
            if not vs: continue
            bbox=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
            parts.append({'name':path+('/color'+str(gi) if len(by_color)>1 else ''),'component_id':component_id,'component_name':path.split('/')[-1],'color':color,'bbox':bbox,**geometry})
            all_vertices.extend(vs)
        if all_vertices:
            bbox=[[min(v[i] for v in all_vertices) for i in range(3)],[max(v[i] for v in all_vertices) for i in range(3)]]
            components.append({'id':component_id,'name':path,'bbox':bbox,'color_groups':len(by_color),'triangles':sum(len(x['faces']) for x in by_color.values())})

    def walk(label, parent_loc, path, inherited=None):
        name=get_name(label) or 'unnamed'
        current_path=path+'/'+name if path else name
        loc=parent_loc.Multiplied(st.GetLocation_s(label))
        inherited=color_of(label) or inherited
        if st.IsReference_s(label):
            referred=TDF_Label()
            st.GetReferredShape_s(label,referred)
            label=referred
        if st.IsAssembly_s(label):
            children=TDF_LabelSequence()
            st.GetComponents_s(label,children)
            for idx in range(1,children.Length()+1):
                walk(children.Value(idx),loc,current_path,inherited)
        else:
            emit_shape(label,loc,current_path,inherited)

    free=TDF_LabelSequence()
    st.GetFreeShapes(free)
    for i in range(1,free.Length()+1): walk(free.Value(i),TopLoc_Location(),'')
    result={'units':'mm','source':input_path.name,'source_sha256':hashlib.sha256(input_path.read_bytes()).hexdigest(),'tessellation':{'linear_mm':0.05,'angular_radians':0.3},'components':components,'parts':parts}
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_text(json.dumps(result,separators=(',',':')),encoding='utf8')
    output_path.with_suffix('.inventory.json').write_text(json.dumps({k:v for k,v in result.items() if k!='parts'},indent=2),encoding='utf8')
    print(f'{output_path}: {len(components)} components, {len(parts)} color meshes, {sum(len(p["faces"]) for p in parts)} triangles')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('input',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    convert(args.input.resolve(),args.output.resolve())
