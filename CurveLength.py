import adsk.core, adsk.fusion, traceback

_app = None
_ui  = None
_handlers = []

class MyCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global selectionInput, text_box_input
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            cmdInput = eventArgs.input

            if cmdInput.id == "selection":
                totalLength = 0
                for iSelection in range(selectionInput.selectionCount):
                    sketch_line = selectionInput.selection(iSelection).entity
                    totalLength += sketch_line.length

                text_box_input.text = f"{totalLength : .4f}"

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
           
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global selectionInput, text_box_input
        try:
            cmd = adsk.core.Command.cast(args.command)

            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            onInputChanged = MyCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)    

            text_box_input = cmd.commandInputs.addTextBoxCommandInput('readonly_textBox', 'Length', 'Start selecting', 2, True)          

            selectionInput = cmd.commandInputs.addSelectionInput('selection', 'Select', 'Basic select command input')
            selectionInput.setSelectionLimits(0)
            selectionInput.addSelectionFilter("SketchCurves")

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        cmdDef = _ui.commandDefinitions.itemById('TotalCurveLength')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('TotalCurveLength', 'Total Curve Length', 'Calculates the total length of a all selected sketch curves')

        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        cmdDef.execute()

        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
