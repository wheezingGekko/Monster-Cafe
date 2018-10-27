

class Debug(object):

    def debugPrint(self, inst, func, msg=None):
        debugMsg = "Error in instance <" + inst + ">: "
        debugMsg += "In " + func + "()"
        if msg is not None:
            debugMsg += "-- " + msg
        print (debugMsg)

