#Author-Scott Noyes
#Description-Tie text objects to model parameters\t

import adsk.core, adsk.fusion, adsk.cam, traceback

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        
        # Clean up old commands
        stop(context)
        
        # Create a button command definition.
        button = cmdDefs.addButtonDefinition('ParametricTextButton', 
                                                   'Parametric Text', 
                                                   'Update sketch texts from model parameters.\n\nUpdates only active component.'
                                                   )
                                                   #,
                                                   #'./resources/Sample')
        
        # Connect to the command created event.
        ParametricTextCreated = ParametricTextCreatedEventHandler()
        button.commandCreated.add(ParametricTextCreated)
        handlers.append(ParametricTextCreated)
        
        # Get the ADD-INS panel in the model workspace. 
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        
        # Add the button to the bottom of the panel.
        buttonControl = addInsPanel.controls.addCommand(button)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class ParametricTextCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command

        # Connect to the execute event.
        onExecute = ParametricTextExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)


# Event handler for the execute event.
class ParametricTextExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        updateSketchTexts()

def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('ParametricTextButton')
        if cmdDef:
            cmdDef.deleteMe()
            
        addinsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addinsPanel.controls.itemById('ParametricTextButton')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            
def updateSketchTexts():
    
    app = adsk.core.Application.get()
    des = app.activeProduct
    for sketch in des.activeComponent.sketches:
        for t in sketch.sketchTexts:
            tParam = t.attributes.itemByName('ParametricText', 'parameterText')
            if tParam:
                p = des.allParameters.itemByName(tParam.value)
            else:
                p = des.allParameters.itemByName(t.text)
                
            if p:
                t.attributes.add('ParametricText', 'parameterText', p.name)
                t.text = des.unitsManager.formatInternalValue(p.value, p.unit)
                
            elif tParam:
                # Text used to have a matching parameter, but it's gone
                # Reset text to original value
                t.text = tParam.value
                tParam.deleteMe()
