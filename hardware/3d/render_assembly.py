# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MACRO12 contributors
# See LICENSE-MIT for the code license. CAD/board licenses are in README.md.
"""Build an editable assembled MACRO12 visualization from source CAD meshes.

Run with Blender 5.2: blender -b --python render_assembly.py -- --preview
All scene coordinates are millimetres; source/reproduction notes accompany it.
"""
import argparse
import gzip
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
args = argparse.ArgumentParser()
args.add_argument('--preview', action='store_true')
args.add_argument('--output', type=Path, default=HERE)
opts = args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
opts.output = opts.output.resolve()
opts.output.mkdir(parents=True, exist_ok=True)
geo = json.loads((HERE/'geometry.json').read_text())
mesh_file = HERE/'assembly-meshes.json.gz'
if mesh_file.exists():
    cad = json.loads(gzip.decompress(mesh_file.read_bytes()))
else:
    cad = json.loads((HERE/'converted-assets/macropad-assembly.json').read_text())
repo = HERE.parent.parent
if not (repo/'docs/images').exists():
    repo = repo/'outputs/macropad-rp2040-easyeda'
textures = HERE/'textures' if (HERE/'textures').exists() else repo/'docs/images'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32 if opts.preview else 128
scene.cycles.use_denoising = True
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    gpu = False
    for device in prefs.devices:
        device.use = device.type != 'CPU'
        gpu |= device.use
    if gpu:
        scene.cycles.device = 'GPU'
except Exception as exc:
    print('CPU render fallback:', exc)
scene.render.resolution_x = 1100 if opts.preview else 2000
scene.render.resolution_y = 1000 if opts.preview else 1800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'

def material(name, color, metallic=0, roughness=.4):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color[:3], 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

green = material('Rev C solder mask', (.025,.11,.045), roughness=.38)
fr4 = material('FR4 laminate edge', (.24,.24,.08), roughness=.6)
black = material('Black engineering plastic', (.014,.018,.023), roughness=.4)
ivory = material('Warm white keycaps - illustrative', (.74,.76,.73), roughness=.3)
teal = material('Teal keycaps - illustrative', (.012,.21,.23), roughness=.28)
white = material('Key legends', (.85,.9,.88), roughness=.6)
metal = material('Brushed nickel', (.52,.55,.58), metallic=.85, roughness=.28)
gold = material('Brass mounting hardware', (.43,.28,.08), metallic=.8, roughness=.3)
glass = material('OLED cover glass', (.003,.005,.008), roughness=.17)

def mesh(name, vertices, faces, mat):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

def bevel(obj, amount, segments=3):
    mod = obj.modifiers.new('Manufactured edge radius', 'BEVEL')
    mod.width = amount
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    return obj

def box(name, pos, size, mat, radius=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if radius:
        bevel(obj, radius)
    return obj

def cylinder(name, xy, bottom, height, radius, mat, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                      depth=height, location=(*xy,bottom+height/2))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj

def tube(name, xy, bottom, height, outer, inner, mat):
    n=64
    vertices=[(xy[0]+r*math.cos(i*2*math.pi/n),xy[1]+r*math.sin(i*2*math.pi/n),z)
              for r,z in [(outer,bottom),(outer,bottom+height),(inner,bottom+height),(inner,bottom)] for i in range(n)]
    faces=[(j*n+i,j*n+(i+1)%n,((j+1)%4)*n+(i+1)%n,((j+1)%4)*n+i) for j in range(4) for i in range(n)]
    return mesh(name,vertices,faces,mat)

def text_obj(name, text, pos, size, mat, align='CENTER'):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = text
    curve.align_x = align
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = .005
    curve.resolution_u = 8
    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    obj.location = pos
    obj.data.materials.append(mat)
    # Save text as geometry so the scene has no external font dependency.
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj.select_set(False)
    return obj

def rounded_ring(width, length, radius, n=12):
    points = []
    for cx,cy,start in [(width/2-radius,length/2-radius,0),
                        (-width/2+radius,length/2-radius,90),
                        (-width/2+radius,-length/2+radius,180),
                        (width/2-radius,-length/2+radius,270)]:
        for j in range(n+1):
            a = math.radians(start+j*90/n)
            points.append((cx+radius*math.cos(a),cy+radius*math.sin(a)))
    return points

def board():
    ring = rounded_ring(59.69,104.14,2.54,16)
    n = len(ring)
    verts = [(x+29.845,y+52.07,z) for z in [-1.6,0] for x,y in ring]
    faces = [tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    obj = mesh('MACRO12 Rev C - exact outline and drilling', verts, faces, fr4)
    cutters = []
    for index,drill in enumerate(geo['drills']):
        if drill['type'] == 'round':
            cutters.append(cylinder('Drill',drill['user_xy'],-2,3,
                                    drill['diameter']/2,black,24))
        else:
            # Capsule slots use the documented center/length and endpoints.
            xy = drill['user_xy']
            width = drill['diameter']
            length = drill['length']
            ring=rounded_ring(length,width,width/2,12)
            n=len(ring)
            cut=mesh('Slot',[(px,py,z) for z in [-2,1] for px,py in ring],
                     [tuple(reversed(range(n))),tuple(range(n,2*n))]+
                     [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],black)
            cut.location.x,cut.location.y=xy
            ends = drill.get('user_ends')
            if ends:
                cut.rotation_euler.z = math.atan2(ends[1][1]-ends[0][1],ends[1][0]-ends[0][0])
            cutters.append(cut)
    for cutout in geo['board']['led_cutouts']:
        cutters.append(box('Routed aperture',(*cutout['user_center_mm'],-.5),
                           (cutout['width_mm'],cutout['height_mm'],3),black))
    bpy.ops.object.select_all(action='DESELECT')
    for cut in cutters:
        cut.select_set(True)
    bpy.context.view_layer.objects.active = cutters[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    tool = bpy.context.object
    mod = obj.modifiers.new('Released Rev C drilled/routed features','BOOLEAN')
    mod.operation='DIFFERENCE'
    mod.solver='EXACT'
    mod.object=tool
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool,do_unlink=True)
    # Boolean cutters may append their material. Reset before assigning faces.
    obj.data.materials.clear()
    obj.data.materials.append(fr4)
    mats=[]
    for side in ['bottom','top']:
        mat = material('Released '+side+' CAM surface',(1,1,1),roughness=.4)
        image_node=mat.node_tree.nodes.new('ShaderNodeTexImage')
        uv_node=mat.node_tree.nodes.new('ShaderNodeUVMap')
        uv_node.uv_map='CAM millimetre registration'
        mat.node_tree.links.new(uv_node.outputs['UV'],image_node.inputs['Vector'])
        image_node.image=bpy.data.images.load(str(textures/(side+'.png')))
        image_node.image.pack()
        mat.node_tree.links.new(image_node.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
        obj.data.materials.append(mat)
        mats.append(mat)
    uv=obj.data.uv_layers.new(name='CAM millimetre registration')
    obj.data.uv_layers.active_index=len(obj.data.uv_layers)-1
    uv.active_render=True
    for poly in obj.data.polygons:
        side = 1 if poly.normal.z>.9 else 2 if poly.normal.z<-.9 else 0
        poly.material_index=side
        for li in poly.loop_indices:
            co=obj.data.vertices[obj.data.loops[li].vertex_index].co
            u=(co.x+1)/61.69 if side!=2 else (59.69-co.x+1)/61.69
            uv.data[li].uv=(u,(co.y+1)/106.14)
    return obj

board()
print('REV_C_BOARD_CREATED',flush=True)

# The official assembly is centered in XY; its user PCB surface is Z3.14.
correction_file = HERE/'alignment.json'
corrections=json.loads(correction_file.read_text())
removed={x['id'] for x in corrections['remove_and_replace_components']}
deltas={x['id']:x['translation_mm'] for x in corrections['per_component_translations']}
palette={}
for part in cad['parts']:
    cid=part['component_id']
    name=part['name']
    # Replace PCB, OLED, encoder and mounting stack with Rev C-specific geometry.
    if cid in removed and cid!=0:
        continue
    color=part['color']
    key=tuple(color)
    if key not in palette:
        is_metal=max(color[:3])-min(color[:3])<.06 and min(color[:3])>.25
        palette[key]=material('Source CAD '+str(key),color,.65 if is_metal else 0,.3 if is_metal else .42)
    mat=black if cid in {0,100} else palette[key]
    delta=deltas.get(cid,[0,0,0])
    verts=[(v[0]+29.845+delta[0],v[1]+52.07+delta[1],v[2]-3.14+delta[2]) for v in part['vertices']]
    if cid==0:
        # Retain the official backplate's plan geometry, correct its stack.
        verts=[(v[0]+29.845,v[1]+52.07,-6.2+(v[2]+6)*1.6/1.57) for v in part['vertices']]
    obj=mesh(name,verts,part['faces'],mat)
    # Preserve source CAD topology; smooth curved surfaces without reshaping it.
    for polygon in obj.data.polygons:
        polygon.use_smooth=True
    obj['source_component_id']=cid
print('SOURCE_ASSEMBLY_IMPORTED',flush=True)

ceramic=material('Generic ceramic passive body',(.35,.24,.13),roughness=.45)
for addition in corrections['add_electronics']:
    ref=addition['ref']
    x,y=addition['user_xy']
    sx,sy,sz=addition['body_size_mm']
    rotation=math.radians(addition['body_user_rotation_deg'])
    part=box(ref+' - representative '+addition['package'],(x,y,-1.6-sz/2),(sx,sy,sz),black if ref.startswith(('R','U')) else ceramic,.08)
    part.rotation_euler.z=rotation
    count=8 if ref=='U3' else 2
    if count==8:
        for side in [-1,1]:
            for i in range(4):
                box(ref+' lead',(x+side*1.95,y+(i-1.5)*.65,-1.8),(.95,.27,.3),metal,.06)
    else:
        for side in [-1,1]:
            px=side*(sx/2-.15)
            terminal=box(ref+' endcap',(x+px*math.cos(rotation),y+px*math.sin(rotation),-1.6-sz/2),(.3,sy+.02,sz+.02),metal,.04)
            terminal.rotation_euler.z=rotation

# A reference 1U symmetric dished keycap, intentionally a cosmetic choice.
for i,key in enumerate(geo['keys_top_to_bottom_left_to_right']):
    x,y=key['user_xy']
    n=52
    rings=[(18.1,18.1,1.1,10.5),(18.1,18.1,1.1,11),
           (13.7,13.7,1.8,18.8)]
    verts=[]
    for width,length,radius,z in rings:
        verts.extend((px+x,py+y,z) for px,py in rounded_ring(width,length,radius))
    faces=[]
    for layer in range(len(rings)-1):
        faces += [(layer*n+j,layer*n+(j+1)%n,(layer+1)*n+(j+1)%n,(layer+1)*n+j) for j in range(n)]
    rim=rounded_ring(13.7,13.7,1.8)
    previous=(len(rings)-1)*n
    for factor in [.8,.6,.4,.2]:
        current=len(verts)
        verts.extend((px*factor+x,py*factor+y,17.9+.9*factor*factor) for px,py in rim)
        faces += [(previous+j,previous+(j+1)%n,current+(j+1)%n,current+j) for j in range(n)]
        previous=current
    center=len(verts)
    verts.append((x,y,17.9))
    faces += [(previous+j,previous+(j+1)%n,center) for j in range(n)]
    cap=mesh('Illustrative keycap F'+str(13+i),verts,faces,teal if key['column']==2 else ivory)
    bevel(cap,.13,3)
    for polygon in cap.data.polygons: polygon.use_smooth=True
    legend=text_obj('Legend F'+str(13+i),'F'+str(13+i),(x,y,20),2.4,white if key['column']==2 else black)
    wrap=legend.modifiers.new('Conform printed legend to dish','SHRINKWRAP')
    wrap.wrap_method='PROJECT'
    wrap.use_project_z=True
    wrap.use_negative_direction=True
    wrap.use_positive_direction=False
    wrap.target=cap
    wrap.offset=.012

# Selected folding OLED glass and required 0.5 mm insulating spacer.
ox,oy=geo['oled']['glass_center_user']
box('OLED insulating spacer - 0.5 mm', (ox,oy,.25),(33.8,22.3,.5),black,.15)
box('ZJY130 folding OLED glass', (ox,oy,1.2),(34.5,23,1.4),glass,.12)
ax0,ay0,ax1,ay1=geo['oled']['user_active_area_bbox']
screen=material('OLED active black',(.0005,.001,.002),roughness=.2)
box('OLED active area',((ax0+ax1)/2,(ay0+ay1)/2,1.91),(ax1-ax0,ay1-ay0,.025),screen)
pixel=material('Simulated OLED white pixels',(.55,.82,.9),roughness=.5)
pbsdf=pixel.node_tree.nodes.get('Principled BSDF')
pbsdf.inputs['Emission Color'].default_value=(.55,.82,.9,1)
pbsdf.inputs['Emission Strength'].default_value=1.4
lines=['MACRO12 / REV C','QMK + VIA','Layer: 0','RGB: ON  Level: 64',
       'Caps:0 Num:0 Scr:0','12 keys + encoder','Audio: disabled','Firmware 0.2.0']
for i,line in enumerate(lines):
    text_obj('Simulated OLED line '+str(i),line,(ax0+.5,ay1-1.0-i*1.75,1.94),1.4,pixel,'LEFT')

# A folding flex passes through the actual routed opening; not a breakout PCB.
flex=material('OLED flex polyimide',(.35,.12,.015),roughness=.45)
box('OLED flex front tail',(18.034,79.8,.08),(11.4,4.0,.12),flex)
box('OLED flex bend through slot',(18.034,77.9085,-1.2),(11.4,.16,2.7),flex)

# Exact shaft center/body rotation from the revised native encoder footprint.
ex,ey=geo['encoder']['user_xy']
enc=box('PEC11R encoder body',(ex,ey,3.25),(12.5,13.4,6.5),metal,.3)
enc.rotation_euler.z=math.radians(45)
box('Encoder phenolic base',(ex,ey,.4),(11.8,12.5,.8),black,.2).rotation_euler.z=math.radians(45)
cylinder('Encoder bushing',(ex,ey),6.5,5,3.5,metal)
cylinder('Encoder 6mm shaft',(ex,ey),6.5,15,3,metal)
# Cosmetic D-shaft knob: 16 mm skirt, 14.5 mm height.
knob=material('Anodized charcoal knob',(.025,.032,.04),metallic=.65,roughness=.32)
bottom=9.0
cylinder('Knob skirt',(ex,ey),bottom,1.2,8,knob,96)
bpy.ops.mesh.primitive_cone_add(vertices=96,radius1=7.4,radius2=5.55,depth=13.3,location=(ex,ey,bottom+1.2+6.65))
bpy.context.object.name='Illustrative D-shaft control knob'
bpy.context.object.data.materials.append(knob)
bevel(bpy.context.object,.25,3)
for i in range(48):
    a=i*2*math.pi/48
    rib=box('Knob grip', (ex+6.3*math.cos(a),ey+6.3*math.sin(a),bottom+8),(.24,.4,8),knob,.1)
    rib.rotation_euler.z=a
box('Knob index',(ex,ey+3.6,bottom+14.52),(.5,3.0,.03),white,.12)

# Mounts remain below the user plane; no screw heads are added in key zones.
mounts=[d for d in geo['drills'] if d['diameter']==4.25]
for index,drill in enumerate(mounts):
    xy=drill['user_xy']
    tube('Solderable M3 nut body '+str(index),xy,-4.6,3,2.78,1.5,gold)
    tube('Nut seating nose '+str(index),xy,-1.6,1.5,2.0,1.5,gold)
    cylinder('M3 x 5 screw head '+str(index),xy,-7.85,1.65,2.85,metal)
    cylinder('M3 x 5 screw shaft '+str(index),xy,-6.2,5,1.5,metal)

stage=material('Warm studio background',(.69,.71,.73),roughness=.75)
box('Studio ground',(29.845,52.07,-8.0),(1500,1500,.2),stage)
world=bpy.data.worlds.new('Soft studio')
scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.8,.85,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.35

def area(name,pos,power,size,target):
    data=bpy.data.lights.new(name,'AREA')
    data.energy=power
    data.shape='DISK'
    data.size=size
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.location=pos
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
area('Large softbox',(-80,-30,180),500000,150,(30,45,0))
area('Edge strip',(100,150,120),650000,100,(30,60,0))
area('Soft fill',(160,-20,80),250000,110,(30,45,0))
data=bpy.data.cameras.new('Assembly hero camera')
camera=bpy.data.objects.new('Assembly hero camera',data)
scene.collection.objects.link(camera)
camera.location=(135,-100,175)
target=Vector((29.845,51,4))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
data.type='ORTHO'
data.ortho_scale=146
data.clip_start=.1
data.clip_end=2000
scene.camera=camera
scene.render.filepath=str(opts.output/('assembled-preview.png' if opts.preview else 'assembled-prototype.png'))
scene['purpose']='Assembly visualization, not an assembly-clearance sign-off or physical prototype photograph'
scene['native_source_sha256']=geo['native_source']['sha256']
scene['keycap_count']=12
bpy.ops.wm.save_as_mainfile(filepath=str(opts.output/'MACRO12-RevC-assembled.blend'))
bpy.ops.render.render(write_still=True)
print('ASSEMBLED_RENDER_SAVED',scene.render.filepath,flush=True)
# Keep the delivered scene portable; packed images do not need local paths.
for image in bpy.data.images:
    if image.packed_file:
        image.filepath='//'+Path(image.filepath).name
scene.render.filepath='//assembled-prototype.png'
bpy.ops.wm.save_as_mainfile(filepath=str(opts.output/'MACRO12-RevC-assembled.blend'))
