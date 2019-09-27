import sys, argparse
import bpy
import pdb

################################
############ Setup #############
################################

parser = argparse.ArgumentParser()
parser.add_argument('--gpu',        default=False,               type=bool, help='gpu-enabled rendering')
parser.add_argument('--staging',    default='staging',           type=str,  help='temp directory for copying ShapeNet files')
parser.add_argument('--output',     default='output/chairs/',   type=str,  help='save directory')
parser.add_argument('--category',   default='random',            type=str,  help='object category (from ShapeNet or primitive, see options in config.py)')
parser.add_argument('--x_res',      default=256,                 type=int,  help='x resolution')
parser.add_argument('--y_res',      default=256,                 type=int,  help='x resolution')
parser.add_argument('--start',      default=0,                   type=int,  help='min image index')
parser.add_argument('--finish',     default=10,                  type=int,  help='max image index')
parser.add_argument('--array_path', default='arrays/shader.npy', type=str,  help='path to array of lighting parameters')
parser.add_argument('--include',    default='.',                 type=str,  help='directory to include in python path')
parser.add_argument('--repeat',     default=10,                  type=int,  help='number of renderings per object')

## ignore the blender arguments
cmd = sys.argv
args = cmd[cmd.index('--')+1:]
args = parser.parse_args(args)

## blender doesn't by default include, the working 
## directory, so add the repo folder manually
sys.path.append(args.include)
print(sys.path)
## grab config parameters from repo folder
import config

## add any other libraries not by default in blender's python
## (e.g., scipy)
sys.path.append(config.include)

## import everything else
import os, math, argparse, scipy.io, scipy.stats, time, random, subprocess, pdb
import numpy as np

## import repo modules
from dataset import BlenderRender, ShapeNetRender, IntrinsicRender, PrimitiveRender
from dataset import utils
# from dataset.BlenderShapenet import BlenderRender, ShapenetRender, IntrinsicRender
# from dataset.PrimitiveRender import PrimitiveRender

## convert params to lists if strings (e.g., '[0,0,0]' --> [0,0,0])
# utils.parse_attributes(args, 'theta_high', 'theta_low', 'pos_high', 'pos_low')

## use a temp folder for copying and manipulating ShapeNet objects
staging = os.path.join(args.staging, str(random.random()))

## choose a renderer based on category
## if from ShapeNet, category is its ID (the mapping is in config.py),
## otherwise category is its name (e.g., Suzanne)
if args.category in config.categories: 
    category = config.categories[args.category] 
    loader = ShapeNetRender(config.shapenet, staging, args.output, create=True)
else:
    category = args.category
    loader = PrimitiveRender()

render_opt = utils.render_parameters[args.category]


################################
########## Rendering ###########
################################

## standard blender operations
blender = BlenderRender(args.gpu)

## rendering intrinsic images along with composite object
intrinsic = IntrinsicRender(args.x_res, args.y_res)

## load light array created with make_array.py
lights = np.load(args.array_path)
# pdb.set_trace()

blender.sphere([0,0,0], 2.5, label = 'sphere')

count = args.start

while count < args.finish:

    ## load a new object from the category
    ## and copy it for shading / shape renderings
    if loader.load(category) == 2:
        print('group label not included! Load next model')
        blender.reset_scene(ignore=['Camera', 'sphere'], gpu=args.gpu)
        continue
    blender.duplicate('shape', 'shape_shading')
    blender.duplicate('shape', 'shape_normals')

    ## render it args.repeat times in different positions and orientations
    for rep in range(args.repeat):
        
        ## get position, orientation, and scale uniformly at random based on high / low from arguments
        blender.translate(['shape', 'shape_shading', 'shape_normals'], render_opt['pos_low'] )
        blender.resize(['shape', 'shape_shading', 'shape_normals'], 3.8)
        blender.rotate(['shape', 'shape_shading', 'shape_normals'], [90, 0, -45])

        ## lighting parameters from array
        energy, lights_pos = lights[22][0], lights[22][1:]
        blender.light(energy, lights_pos)
        blender.add_light(1.0 * lights[2][0], lights[2][1:])

        ## render the composite image and intrinsic images
        for mode in ['composite']:  # 'composite', 'lights'
            filename = str(count) + '_' + mode 
            intrinsic.changeMode(mode)
            bpy.context.scene.render.alpha_mode = 'TRANSPARENT'  # use transparent background
            blender.write(args.output, filename)
        count += 1

    ## delete object
    # blender.delete(lambda x: x.name in ['shape', 'shape_shading', 'shape_normals'])
    # blender.delete(lambda x: x.name not in ['Camera', 'sphere'])
    blender.reset_scene(ignore=['Camera','sphere'], gpu=args.gpu)
    # blender.write(args.output, filename+'-null.png')


################################
########## Reference ###########
################################

#### create a sphere as a shape / shading reference
blender.sphere([0,0,0], 2.5)
blender.duplicate('shape', 'shape_shading')
blender.duplicate('shape', 'shape_normals')

## light it
energy = lights[22][0]
position = lights[22][1:]
blender.light(energy, position)
blender.add_light(1.0 * lights[2][0], lights[2][1:])

## render it
# mode_set = ['composite', 'albedo', 'depth', 'depth_hires', 'normals', 'shading', 'mask', 'specular']
for mode in ['composite']:
    filename = 'sphere_' + mode 
    intrinsic.changeMode(mode)
    bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
    blender.write(args.output, filename)

## delete it
blender.delete(lambda x: x.name in ['shape'] )




