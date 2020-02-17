from sfgen import *

InkscapePath = "/Applications/Inkscape.app/Contents/Resources/bin/inkscape"
CuraPath = "/Applications/Cura/Cura.app"
OpenSCADPath = "/Applications/OpenSCAD.app"

def check_basecut(svgfn):
    # ensure there is only one path
    svg = parse(svgfn)
    for (cnt, node) in enumerate(svg.getElementsByTagName("path")):
        if cnt > 0:
            return False
    return True

def merge_svg(file_list, color_list, outfn):
    first = None
    idx = 0
    for (svgfn, color) in zip(file_list, color_list):
        svg = parse(svgfn)
        for node in svg.getElementsByTagName("g"):
            if idx == 0:
                # cut layer
                # write a new group
                container = svg.createElement("g")
                container.setAttribute("transform", node.attributes["transform"].nodeValue)
                node.parentNode.replaceChild(container, node)
                container.appendChild(node)
                node.attributes["fill"] = "none"
                node.attributes["stroke"] = "rgb(0, 0, 255)"
                node.attributes["stroke-opacity"] = "1"
                node.attributes["stroke-width"] = ".01mm"
            else:
                node.attributes["fill"] = color
            del node.attributes["transform"]
            idx += 1
            import_nodes = svg.importNode(node, True)
            container.appendChild(import_nodes)
            if first == None:
                first = svg
    f = open(outfn, 'w')
    f.write(first.toxml())

def potrace(svgfn, fn, turd=None, size=None):
    cmd = ["potrace", "-i", "-b", "svg"]
    if turd != None:
        cmd.extend(["-t", str(turd)])
    if size != None:
        sz = map(str, size)
        cmd.extend(["-W", sz[0], "-H", sz[1]])
    cmd.extend(["-o", svgfn, fn])
    cmd = str.join(' ', cmd)
    msg = "Running '%s'" % cmd
    log(msg)
    os.system(cmd)

# laser cutter pipeline
def pipeline_lasercutter(args, lattice, inches=3, dpi=96, turd=10):
    # layers
    rs = RenderSnowflake(lattice)
    name = str.join('', [c for c in args.name if c.islower()])
    size = args.target_size
    layerfn = "%s_layer_%%d.bmp" % name
    resize = inches * dpi
    print "***Attempting to save layers as BMP images***"
    fnlist = rs.save_layers(layerfn, 2, resize=resize, margin=1)
    # we want to drop the heaviest layer
    del fnlist[0]
    #
    # try to save o'natural
    print "***Attempting to generate BMP image***"
    imgfn = "%s_bw.bmp" % name
    lattice.save_image(imgfn, scheme=BlackWhite(lattice), resize=resize, margin=1)
    #
    print "***Attempting to generate SVG using potrace***"
    svgfn = "%s_bw.svg" % name
    potrace(svgfn, imgfn, turd=2000)
    if not check_basecut(svgfn):
        msg = "There are disconnected elements in the base cut, turning on boundary layer."
        log(msg)
        lattice.save_image(imgfn, scheme=BlackWhite(lattice, boundary=True), resize=resize, margin=1)
        potrace(svgfn, imgfn, turd=2000)
        assert check_basecut(svgfn), "Despite best efforts, base cut is still non-contiguous."
    os.unlink(svgfn)
    fnlist.insert(0, imgfn)
    # adjusted for ponoko
    # cut layer is blue
    # etch layer are black, or shades of grey
    colors = ["#000000", "#111111", "#222222", "#333333", "#444444", "#555555"]
    svgs = []
    for (idx, fn) in enumerate(fnlist):
        svgfn = os.path.splitext(fn)[0]
        svgfn = "%s_laser.svg" % svgfn
        svgs.append(svgfn)
        if idx == 0:
            potrace(svgfn, fn, turd=turd, size=size)
        else:
            potrace(svgfn, fn, size=size)
    #
    print "***Attempting to merge SVG images***"
    svgfn = "%s_laser_merged.svg" % name
    merge_svg(svgs, colors, svgfn)
    #
    """
    # move to eps
    cmd = "%s %s -E %s" % (InkscapePath, svgfn, epsfn)
    msg = "Running '%s'" % cmd
    log(msg)
    os.system(cmd)
    """

# 3d pipeline
def pipeline_3d(args, lattice, inches=3, dpi=96, turd=10):
    # layers
    rs = RenderSnowflake(lattice)
    name = str.join('', [c for c in args.name if c.islower()])
    size = args.target_size
    layerfn = "%s_layer_%%d.bmp" % name
    resize = inches * dpi
    print "***Attempting to save layers as BMP images***"
    fnlist = rs.save_layers(layerfn, 5, resize=resize, margin=1)
    # we want to drop the heaviest layer
    #print "***Deleting BMP layer index 0 %s" % fnlist[0]
    #os.remove(fnlist[0])
    del fnlist[0]
    #
    # try to save o'natural
    print "***Attempting to generate BMP image***"
    imgfn = "%s_bw.bmp" % name
    #lattice.save_image(imgfn, scheme=BlackWhite(lattice), resize=resize, margin=1)
    lattice.save_image(imgfn, scheme=Grayscale(lattice), resize=resize, margin=1)
    #
    print "***Attempting to generate SVG using potrace***"
    svgfn = "%s_bw.svg" % args.name
    potrace(svgfn, imgfn, turd=2000)
    if not check_basecut(svgfn):
        msg = "There are disconnected elements in the base cut, turning on boundary layer."
        log(msg)
        lattice.save_image(imgfn, bw=True, boundary=True)
        potrace(svgfn, imgfn, turd=2000)
        assert check_basecut(svgfn), "Despite best efforts, base cut is still non-contiguous."
    #
    print "***Deleting SVG %s" % svgfn
    os.unlink(svgfn)
    fnlist.insert(0, imgfn)
    #
    print "***Attempting to turn BMP layers into SVG images***"
    epsList = []
    for (idx, fn) in enumerate(fnlist):
        epsfn = os.path.splitext(fn)[0]
        epsfn = "%s_bmp.eps" % epsfn
        epsList.append(epsfn)
        cmd = "potrace -M .1 --tight -i -b eps -o %s %s" % (epsfn, fn)
        #if idx == 0:
        #     potrace(svgfn, fn, turd=turd, size=size)
        # else:
        #     potrace(svgfn, fn, size=size)
        msg = "Running '%s'" % cmd
        log(msg)
        os.system(cmd)
    #
    print "***Attempting to generate DXF using pstoedit"
    dxfList=[]
    for (idx, epsfn) in enumerate(epsList):
        dxffn = os.path.splitext(epsfn)[0]
        dxffn = "%s_eps.dxf" % dxffn
        dxfList.append(dxffn)
        #on windows it _needs_ to have the dxf part in double quotes
        #STH 2018.0212
        cmd = 'pstoedit -dt -f "dxf:-polyaslines -mm" %s %s' % (epsfn, dxffn)
        msg = "Running '%s'" % cmd
        log(msg)
        os.system(cmd)
    #
    print "***Attempting to generate a STL using OpenSCAD***"
    scad_fn = "%s_3d.scad" % args.name
    f = open(scad_fn, 'w')
    for (idx, dxffn) in enumerate(dxfList,1):
        scad_txt = 'scale([30, 30, 30]) linear_extrude(height=%f, layer="0") import("%s");\n' % (idx*0.18, dxffn)
        f.write(scad_txt)
    f.close()
    stlfn = "%s_3d.stl" % args.name
    if sys.platform=="win32":
        cmd = "openscad.com -o %s %s" % (stlfn, scad_fn)
    else:
        cmd = "%s/Contents/MacOS/OpenSCAD -o %s %s" % (OpenSCADPath, stlfn, scad_fn)
    msg = "Running '%s'" % cmd
    log(msg)
    os.system(cmd)
    #
    #print "***Attempting to generate a gcode using CURA***"
    #print "***THIS IS AN UNRESOLVED ISSUE***"
    #cmd = "python %s/Contents/Resources/cura.py -s %s -i %s" % (CuraPath, stlfn, SNOWFLAKE_INI)
    #msg = "Running '%s'" % cmd
    #log(msg)
    #os.system(cmd)




