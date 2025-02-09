import adsk.core, adsk.fusion, traceback

_app = None
_ui  = None
_handlers = []
           
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MyExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args: adsk.core.CommandEventArgs):
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        
        # Get the active design
        design = _app.activeProduct
        if not isinstance(design, adsk.fusion.Design):
            _ui.messageBox('No active Fusion 360 design', 'Error')
            return
        
        # Get the active sketch the user is currently editing
        sketch = _app.activeEditObject
        if not isinstance(sketch, adsk.fusion.Sketch):
            _ui.messageBox('No active sketch found', 'Error')
            return
        
        # Find the selected SketchFittedSpline
        selectedSpline = None
        for entity in _ui.activeSelections:
            if isinstance(entity.entity, adsk.fusion.SketchFittedSpline):
                selectedSpline = entity.entity
                break
        
        if not selectedSpline:
            _ui.messageBox('No SketchFittedSpline selected', 'Error')
            return
        
        # Clear the selection before creating the point
        _ui.activeSelections.clear()
        
        # Get the slider value
        positionRatio = positionInput.value
        
        # Get the spline evaluator
        evaluator = selectedSpline.geometry.evaluator
        length = selectedSpline.length
        targetLength = length * positionRatio
        
        # Find the parameter at the selected length
        success, param = evaluator.getParameterAtLength(0, targetLength)
        if not success:
            _ui.messageBox('Failed to find parameter at specified length', 'Error')
            return
        
        # Get the point at that parameter
        success, point = evaluator.getPointAtParameter(param)
        if not success:
            _ui.messageBox('Failed to get point at parameter', 'Error')
            return
        
        # Add the calculated point to the sketch
        sketchPoints = sketch.sketchPoints
        sketchPoints.add(point)


class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global selectionInput, positionInput
        try:
            cmd = adsk.core.Command.cast(args.command)

            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)      

            selectionInput = cmd.commandInputs.addSelectionInput('selection', 'Select', 'Basic select command input')
            selectionInput.setSelectionLimits(1)
            selectionInput.addSelectionFilter("SketchCurves")

            inputs = cmd.commandInputs
        
            # Add a slider to select position along the spline
            positionInput = inputs.addFloatSpinnerCommandInput('spinnerFloat', 'Position', '', 0 , 1 , 0.01, 0.5)

            
            onExecute = MyExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        cmdDef = _ui.commandDefinitions.itemById('PointAtLengthRatio')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('PointAtLengthRatio', 'Point At Length Ratio', 'Places a point on the selected curve at specified length ratio')

        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)


        cmdDef.execute()

        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
