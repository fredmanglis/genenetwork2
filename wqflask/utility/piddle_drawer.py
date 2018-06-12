from __future__ import print_function

import sys
import json
import argparse
import piddle as pid

def print_help(args, parser):
    print(parser.format_help())

def generate_data_parser(args, parser):
    print("Generating data parser...")

def parse_offset(offset_str):
    offset = tuple(map(int, offset_str.split(",")))
    return offset

def bar_plotter(args):
    canvas = pid.PILCanvas(size=(args.canvaslength,args.canvaswidth))
    data = json.loads(args.data)
    barcolour = get_colour(args.barcolor)
    axescolour = get_colour(args.axescolor)
    labelcolour = get_colour(args.labelcolor)
    xlabel = args.xlabel
    ylabel = args.ylabel
    title = args.title
    offset = parse_offset(args.offset)
    zoom = args.zoom
    filename = args.filename
    imgformat = args.imgformat
    plotBar(canvas, data, barColor=barcolour, axesColor=axescolour,
            labelColor=labelcolour, XLabel=None, YLabel=None, title=None,
            offset=(60, 20, 40, 40), zoom = 1)
    canvas.save(filename, format=imgformat);

def int_mapping_plotter(args):
    data = json.loads(args.data)
    canvas = pid.PILCanvas(size=(args.canvaslength,args.canvaswidth))
    offset = parse_offset(args.offset)
    zoom = args.zoom
    startmb = args.startmb
    endmb = args.endmb
    showfocusform = args.showlocusform
    plotIntMapping(data, canvas, offset=offset, zoom=zoom, startMb=startmb,
                   endMb=endmv, showLocusForm = "")

def get_colour(colour_str):
    colour = None
    if colour_str.startswith("0x"):
        print("It's a hex colour")
        colour = pid.HexColor(int(colour_str, 16))
    else:
        colour = pid.__dict__.get(colour_str)

    if colour:
        return colour
    else:
        raise RuntimeError("Invalid colour: "+colour_str)

def select_action(args, parser):
    actions = {
        "plotbar": bar_plotter,
        "plotintmapping", int_mapping_plotter
    }
    fn = actions.get(args.action, None)
    fn(args)

# You can run this with something like
# python -m wqflask.utility.piddle_drawer plotbar /tmp/test.png --data "{\
#    \"key1\":\"value1\",
#    \"key2\":\"value2\"
#    }"
if __name__ == '__main__':
    desc = """
piddle_drawer - This is an attempt to replace usage of the piddle module  with a
                standalone and external python2 program that can be called on
                the command-line to draw diagrams.
"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("action", help="Select the action to take.",
                        choices=["plotbar", "plotintmapping"])
    parser.add_argument("filename", help="Filename of generated image")
    parser.add_argument("--imgformat", help="Format of generated image",
                        default="gif", choices=["gif", "png", "bmp"])
    parser.add_argument("-t", "--title", help="Title for the generated image",
                        default="untitled")
    parser.add_argument("-cvl", "--canvaslength", help="""Length of canvas (
default: 400)""", default=400, type=int)
    parser.add_argument("-cvw", "--canvaswidth", help="""Width of canvas (
default: 300)""", default=300, type=int)
    parser.add_argument("-bc", "--barcolor",
                        help="The bar graph colour (default: blue)",
                        default="blue")
    parser.add_argument("-ac", "--axescolor",
                        help="The colour of axes (default: black)",
                        default="black")
    parser.add_argument("-lc", "--labelcolor",
                        help="The colour of label (default: black)",
                        default="black")
    parser.add_argument("-xl", "--xlabel", help="The label for the X-axis")
    parser.add_argument("-yl", "--ylabel", help="The label for the Y-axis")
    parser.add_argument("-o", "--offset", help="""Offset in the form: xleft,
    xright,ytop,ybottom (default 60,20,40,40)""", default="60,20,40,40")
    parser.add_argument("-z", "--zoom", help="Zoom level (default: 1)",
                        default=1, type=int)
    parser.add_argument("-d", "--data", help="Pickled string of data to process"
                        , type=str)
    parser.add_argument("-sm", "--startmb", help="startMb", default=None)
    parser.add_argument("em", "--endmb", help="endMb", default=None)
    parser.add_argument("-sl", "--showlocusform", help="showLocusForm",
                        default="")

    args = parser.parse_args()
    select_action(args, parser)

# Initially from wqflask/utility/Plot.py
def plotBar(canvas, data, barColor=pid.blue, axesColor=pid.black, labelColor=pid.black, XLabel=None, YLabel=None, title=None, offset= (60, 20, 40, 40), zoom = 1):
    xLeftOffset, xRightOffset, yTopOffset, yBottomOffset = offset

    plotWidth = canvas.size[0] - xLeftOffset - xRightOffset
    plotHeight = canvas.size[1] - yTopOffset - yBottomOffset
    if plotHeight<=0 or plotWidth<=0:
       return

    if len(data) < 2:
       return

    max_D = max(data)
    min_D = min(data)
    #add by NL 06-20-2011: fix the error: when max_D is infinite, log function in detScale will go wrong
    if max_D == float('inf') or max_D>webqtlConfig.MAXLRS:
       max_D=webqtlConfig.MAXLRS #maximum LRS value

    xLow, xTop, stepX = detScale(min_D, max_D)

    #reduce data
    #ZS: Used to determine number of bins for permutation output
    step = ceil((xTop-xLow)/50.0)
    j = xLow
    dataXY = []
    Count = []
    while j <= xTop:
       dataXY.append(j)
       Count.append(0)
       j += step

    for i, item in enumerate(data):
       if item == float('inf') or item>webqtlConfig.MAXLRS:
           item = webqtlConfig.MAXLRS #maximum LRS value
       j = int((item-xLow)/step)
       Count[j] += 1

    yLow, yTop, stepY=detScale(0,max(Count))

    #draw data
    xScale = plotWidth/(xTop-xLow)
    yScale = plotHeight/(yTop-yLow)
    barWidth = xScale*step

    for i, count in enumerate(Count):
       if count:
           xc = (dataXY[i]-xLow)*xScale+xLeftOffset
           yc =-(count-yLow)*yScale+yTopOffset+plotHeight
           canvas.drawRect(xc+2,yc,xc+barWidth-2,yTopOffset+plotHeight,edgeColor=barColor,fillColor=barColor)

    #draw drawing region
    canvas.drawRect(xLeftOffset, yTopOffset, xLeftOffset+plotWidth, yTopOffset+plotHeight)

    #draw scale
    scaleFont=pid.Font(ttf="cour",size=11,bold=1)
    x=xLow
    for i in range(int(stepX)+1):
       xc=xLeftOffset+(x-xLow)*xScale
       canvas.drawLine(xc,yTopOffset+plotHeight,xc,yTopOffset+plotHeight+5, color=axesColor)
       strX = cformat(d=x, rank=0)
       canvas.drawString(strX,xc-canvas.stringWidth(strX,font=scaleFont)/2,yTopOffset+plotHeight+14,font=scaleFont)
       x+= (xTop - xLow)/stepX

    y=yLow
    for i in range(int(stepY)+1):
       yc=yTopOffset+plotHeight-(y-yLow)*yScale
       canvas.drawLine(xLeftOffset,yc,xLeftOffset-5,yc, color=axesColor)
       strY = "%d" %y
       canvas.drawString(strY,xLeftOffset-canvas.stringWidth(strY,font=scaleFont)-6,yc+5,font=scaleFont)
       y+= (yTop - yLow)/stepY

    #draw label
    labelFont=pid.Font(ttf="tahoma",size=17,bold=0)
    if XLabel:
       canvas.drawString(XLabel,xLeftOffset+(plotWidth-canvas.stringWidth(XLabel,font=labelFont))/2.0,
               yTopOffset+plotHeight+yBottomOffset-10,font=labelFont,color=labelColor)

    if YLabel:
       canvas.drawString(YLabel, 19, yTopOffset+plotHeight-(plotHeight-canvas.stringWidth(YLabel,font=labelFont))/2.0,
               font=labelFont,color=labelColor,angle=90)

    labelFont=pid.Font(ttf="verdana",size=16,bold=0)
    if title:
       canvas.drawString(title,xLeftOffset+(plotWidth-canvas.stringWidth(title,font=labelFont))/2.0,
               20,font=labelFont,color=labelColor)

# Initially from wqflask/wqflask/marker_regression/marker_regression_gn1.py
def plotIntMapping(data, canvas, offset= (80, 120, 20, 100), zoom = 1, startMb = None, endMb = None, showLocusForm = ""):
    #calculating margins
    xLeftOffset, xRightOffset, yTopOffset, yBottomOffset = offset
    if data.get("multipleInterval"):
        yTopOffset = max(80, yTopOffset)
    else:
        if data.get("legendChecked"):
            yTopOffset = max(80, yTopOffset)
        else:
            pass

    if data.get("plotScale") != 'physic':
        yBottomOffset = max(120, yBottomOffset)
    fontZoom = zoom
    if zoom == 2:
        xLeftOffset += 20
        fontZoom = 1.5

    xLeftOffset = int(xLeftOffset*fontZoom)
    xRightOffset = int(xRightOffset*fontZoom)
    yBottomOffset = int(yBottomOffset*fontZoom)

    cWidth = canvas.size[0]
    cHeight = canvas.size[1]
    plotWidth = cWidth - xLeftOffset - xRightOffset
    plotHeight = cHeight - yTopOffset - yBottomOffset

    #Drawing Area Height
    drawAreaHeight = plotHeight
    if data.get("plotScale") == 'physic' and data.get("selectedChr") > -1:
        drawAreaHeight -= data.get("ENSEMBL_BAND_HEIGHT") + data.get("UCSC_BAND_HEIGHT") + data.get("WEBQTL_BAND_HEIGHT") + 3*data.get("BAND_SPACING") + 10*zoom
        if data.get("geneChecked"):
            drawAreaHeight -= data.get("NUM_GENE_ROWS")*data.get("EACH_GENE_HEIGHT") + 3*data.get("BAND_SPACING") + 10*zoom
    else:
        if data.get("selectedChr") > -1:
            drawAreaHeight -= 20
        else:
            drawAreaHeight -= 30

        ## BEGIN HaplotypeAnalyst
    if data.get("haplotypeAnalystChecked") and data.get("selectedChr") > -1:
        drawAreaHeight -= data.get("EACH_GENE_HEIGHT") * (data.get("NR_INDIVIDUALS")+10) * 2 * zoom
    ## END HaplotypeAnalyst

    if zoom == 2:
        drawAreaHeight -= 60

    #Image map
    gifmap = HT.Map(name = "WebQTLImageMap")

    newoffset = (xLeftOffset, xRightOffset, yTopOffset, yBottomOffset)
    # Draw the alternating-color background first and get plotXScale
    plotXScale = drawGraphBackground(canvas, gifmap, offset=newoffset, zoom= zoom, startMb=startMb, endMb = endMb)

    #draw bootstap
    if data.get("bootChecked") and not data.get("multipleInterval") and not data.get("manhattan_plot"):
        drawBootStrapResult(canvas, data.get("nboot"), drawAreaHeight, plotXScale, offset=newoffset, zoom= zoom, startMb=startMb, endMb = endMb)

    # Draw clickable region and gene band if selected
    if data.get("plotScale") == 'physic' and data.get("selectedChr") > -1:
        drawClickBand(canvas, gifmap, plotXScale, offset=newoffset, zoom = zoom, startMb=startMb, endMb = endMb)
        if data.get("geneChecked") and data.get("geneCol"):
            drawGeneBand(canvas, gifmap, plotXScale, offset=newoffset, zoom = zoom, startMb=startMb, endMb = endMb)
        if data.get("SNPChecked"):
            drawSNPTrackNew(canvas, offset=newoffset, zoom = 2*zoom, startMb=startMb, endMb = endMb)
        ## BEGIN HaplotypeAnalyst
        if data.get("haplotypeAnalystChecked"):
            drawHaplotypeBand(canvas, gifmap, plotXScale, offset=newoffset, zoom = zoom, startMb=startMb, endMb = endMb)
        ## END HaplotypeAnalyst

    # Draw X axis
    drawXAxis(canvas, drawAreaHeight, gifmap, plotXScale, showLocusForm, offset=newoffset, zoom = zoom, startMb=startMb, endMb = endMb)
    # Draw QTL curve
    drawQTL(canvas, drawAreaHeight, gifmap, plotXScale, offset=newoffset, zoom= zoom, startMb=startMb, endMb = endMb)

    #draw legend
    if data.get("multipleInterval"):
        drawMultiTraitName(fd, canvas, gifmap, showLocusForm, offset=newoffset)
    elif data.get("legendChecked"):
        drawLegendPanel(canvas, offset=newoffset, zoom = zoom)
    else:
        pass

    #draw position, no need to use a separate function
    drawProbeSetPosition(canvas, plotXScale, offset=newoffset, zoom = zoom)

    return gifmap

def drawBootStrapResult(data, canvas, nboot, drawAreaHeight, plotXScale, offset= (40, 120, 80, 10), zoom = 1, startMb = None, endMb = None):
    xLeftOffset, xRightOffset, yTopOffset, yBottomOffset = offset
    plotWidth = canvas.size[0] - xLeftOffset - xRightOffset
    plotHeight = canvas.size[1] - yTopOffset - yBottomOffset
    yZero = canvas.size[1] - yBottomOffset
    fontZoom = zoom
    if zoom == 2:
        fontZoom = 1.5

    bootHeightThresh = drawAreaHeight*3/4

    #break bootstrap result into groups
    BootCoord = []
    i = 0
    startX = xLeftOffset

    if data.get("selectedChr") == -1: #ZS: If viewing full genome/all chromosomes
        for j, _chr in enumerate(data.get("genotype")):
            BootCoord.append( [])
            for _locus in _chr:
                if data.get("plotScale") == 'physic':
                    Xc = startX + (_locus.Mb-data.get("startMb"))*plotXScale
                else:
                    Xc = startX + (_locus.cM-_chr[0].cM)*plotXScale
                BootCoord[-1].append([Xc, data.get("bootResult")[i]])
                i += 1
            startX += (data.get("ChrLengthDistList")[j] + data.get("GraphInterval"))*plotXScale
    else:
        for j, _chr in enumerate(data.get("genotype")):
            if _chr.name == data.get("ChrList")[data.get("selectedChr")][0]:
                BootCoord.append( [])
            for _locus in _chr:
                if _chr.name == data.get("ChrList")[data.get("selectedChr")][0]:
                    if data.get("plotScale") == 'physic':
                        Xc = startX + (_locus.Mb-startMb)*plotXScale
                    else:
                        Xc = startX + (_locus.cM-_chr[0].cM)*plotXScale
                    BootCoord[-1].append([Xc, data.get("bootResult")[i]])
                i += 1

    #reduce bootResult
    if data.get("selectedChr") > -1:
        maxBootBar = 80.0
    else:
        maxBootBar = 200.0
    stepBootStrap = plotWidth/maxBootBar
    reducedBootCoord = []
    maxBootCount = 0

    for BootChrCoord in BootCoord:
        nBoot = len(BootChrCoord)
        bootStartPixX = BootChrCoord[0][0]
        bootCount = BootChrCoord[0][1]
        for i in range(1, nBoot):
            if BootChrCoord[i][0] - bootStartPixX < stepBootStrap:
                bootCount += BootChrCoord[i][1]
                continue
            else:
                if maxBootCount < bootCount:
                    maxBootCount = bootCount
                # end if
                reducedBootCoord.append([bootStartPixX, BootChrCoord[i][0], bootCount])
                bootStartPixX = BootChrCoord[i][0]
                bootCount = BootChrCoord[i][1]
            # end else
        # end for
        #add last piece
        if BootChrCoord[-1][0] - bootStartPixX  > stepBootStrap/2.0:
            reducedBootCoord.append([bootStartPixX, BootChrCoord[-1][0], bootCount])
        else:
            reducedBootCoord[-1][2] += bootCount
            reducedBootCoord[-1][1] = BootChrCoord[-1][0]
        # end else
        if maxBootCount < reducedBootCoord[-1][2]:
            maxBootCount = reducedBootCoord[-1][2]
        # end if
    for item in reducedBootCoord:
        if item[2] > 0:
            if item[0] < xLeftOffset:
                item[0] = xLeftOffset
            if item[0] > xLeftOffset+plotWidth:
                item[0] = xLeftOffset+plotWidth
            if item[1] < xLeftOffset:
                item[1] = xLeftOffset
            if item[1] > xLeftOffset+plotWidth:
                item[1] = xLeftOffset+plotWidth
            if item[0] != item[1]:
                canvas.drawRect(item[0], yZero, item[1],
                                yZero - item[2]*bootHeightThresh/maxBootCount,
                                fillColor=data.get("BOOTSTRAP_BOX_COLOR"))

    ###draw boot scale
    highestPercent = (maxBootCount*100.0)/nboot
    bootScale = Plot.detScale(0, highestPercent)
    bootScale = Plot.frange(bootScale[0], bootScale[1], bootScale[1]/bootScale[2])
    bootScale = bootScale[:-1] + [highestPercent]

    bootOffset = 50*fontZoom
    bootScaleFont=pid.Font(ttf="verdana",size=13*fontZoom,bold=0)
    canvas.drawRect(canvas.size[0]-bootOffset,yZero-bootHeightThresh,canvas.size[0]-bootOffset-15*zoom,yZero,fillColor = pid.yellow)
    canvas.drawLine(canvas.size[0]-bootOffset+4, yZero, canvas.size[0]-bootOffset, yZero, color=pid.black)
    canvas.drawString('0%' ,canvas.size[0]-bootOffset+10,yZero+5,font=bootScaleFont,color=pid.black)
    for item in bootScale:
        if item == 0:
            continue
        bootY = yZero-bootHeightThresh*item/highestPercent
        canvas.drawLine(canvas.size[0]-bootOffset+4,bootY,canvas.size[0]-bootOffset,bootY,color=pid.black)
        canvas.drawString('%2.1f'%item ,canvas.size[0]-bootOffset+10,bootY+5,font=bootScaleFont,color=pid.black)

    if data.get("legendChecked"):
        startPosY = 30
        nCol = 2
        smallLabelFont = pid.Font(ttf="trebuc", size=12*fontZoom, bold=1)
        leftOffset = xLeftOffset+(nCol-1)*200
        canvas.drawRect(leftOffset,startPosY-6, leftOffset+12,startPosY+6, fillColor=pid.yellow)
        canvas.drawString('Frequency of the Peak LRS',leftOffset+ 20, startPosY+5,font=smallLabelFont,color=pid.black)
