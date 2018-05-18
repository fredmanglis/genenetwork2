from __future__ import print_function

import sys
import cPickle
import argparse
import piddle as pid

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


def print_help(args, parser):
    print(parser.format_help())

def generate_data_parser(args, parser):
    print("Generating data parser...")

def bar_plotter(args):
    barcolour = get_colour(args.barcolor)
    axescolour = get_colour(args.axescolor)
    print("RAW DATA =======>", args.data)
    data = unpickle(args.data)
    print("DATA:", data)
    print("ARGS:", args)

def get_canvas(args):
    size=(args.canvaslength, args.canvaswidth)
    canvas = pid.PILCanvas(size=size)
    return cPickle.dumps(canvas)

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

def pickle(obj):
    return cPickle.dumps(obj)

def unpickle(raw_data):
    return cPickle.loads(raw_data)

def select_action(args, parser):
    actions = {
        "plotbar": bar_plotter,
        "getcanvas": get_canvas
    }
    fn = actions.get(args.action, None)
    fn(args)

# You can run this with something like
# python -m wqflask.utility.piddle_drawer plotbar /tmp/test.png --data "(lp1
# S'this'
# p2
# aS'is'
# p3
# aS'the'
# p4
# aS'data'
# p5
# a."
if __name__ == '__main__':
    desc = """
piddle_drawer - This is an attempt to replace usage of the piddle module  with a
                standalone and external python2 program that can be called on
                the command-line to draw diagrams.
"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("action", help="Select the action to take.",
                        choices=["plotbar"])
    parser.add_argument("filename", help="Filename of generated image")
    parser.add_argument("--imgformat", help="Format of generated image",
                        default="gif", choices=["gif", "png", "bmp"])
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
    parser.add_argument("-xl", "--xlabel", help="The label for the X-axis")
    parser.add_argument("-yl", "--ylabel", help="The label for the Y-axis")
    parser.add_argument("-o", "--offset", help="""Offset in the form: xleft,
    xright,ytop,ybottom (default 60,20,40,40)""", default="60,20,40,40")
    parser.add_argument("-z", "--zoom", help="Zoom level (default: 1)",
                        default=1, type=int)
    parser.add_argument("-d", "--data", help="Pickled string of data to process"
                        , type=str)

    args = parser.parse_args()
    select_action(args, parser)
