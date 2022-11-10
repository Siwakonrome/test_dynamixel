from dynamixel_sdk import *             


ADDR_PRO_TORQUE_ENABLE      = 64               
ADDR_PRO_GOAL_POSITION      = 116
ADDR_PRO_PRESENT_POSITION   = 132
PROTOCOL_VERSION            = 1.0              
DXL_ID                      = 1                 
BAUDRATE                    = 57600             
DEVICENAME                  = '/dev/ttyUSB0'    
TORQUE_ENABLE               = 1                 
TORQUE_DISABLE              = 0     
DXL_MINIMUM_POSITION_LIMIT  = 180          
DXL_MAXIMUM_POSITION_LIMIT  = 1800 
DXL_MINIMUM_POSITION_VALUE  = 0   
DXL_MAXIMUM_POSITION_VALUE  = 4095 
DXL_MOVING_STATUS_THRESHOLD = 10           






class DynamixelDriver:
    def __init__(self) -> None:
        self.from_current_position = None
        self.dxl_present_position = DXL_MINIMUM_POSITION_LIMIT
        self.dxl_goal_position = [DXL_MINIMUM_POSITION_LIMIT, DXL_MAXIMUM_POSITION_LIMIT]        
        self.portHandler = PortHandler(DEVICENAME)
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)     
        self.open_the_port()
        self.change_the_baudrate()

    def open_the_port(self) -> None:
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")

    def change_the_baudrate(self) -> None:
        if self.portHandler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")

    def dxl_position_to_degree(self, dxl : int) -> float:
        y_intercept : float = 360.0 - ( ( 360.0 / (DXL_MAXIMUM_POSITION_VALUE - DXL_MINIMUM_POSITION_VALUE) ) * DXL_MAXIMUM_POSITION_VALUE)
        degree : float = ( 360.0 / (DXL_MAXIMUM_POSITION_VALUE - DXL_MINIMUM_POSITION_VALUE) ) * dxl + y_intercept
        return degree 

    def degree_to_dxl_position(self, degree : float) -> int:
        y_intercept : float = DXL_MAXIMUM_POSITION_VALUE - ( ( (DXL_MAXIMUM_POSITION_VALUE - DXL_MINIMUM_POSITION_VALUE) / 360.0 ) * 360.0)
        dxl_position : float =  ( (DXL_MAXIMUM_POSITION_VALUE - DXL_MINIMUM_POSITION_VALUE) / 360.0 )  * degree + y_intercept
        return int(dxl_position)

    def get_current_position(self) -> dict:
        self.dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, DXL_ID, ADDR_PRO_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            return {"position" : self.dxl_present_position, "comm" : dxl_comm_result, "error" : dxl_error, "ret" : False}
        elif dxl_error != 0:
            return {"position" : self.dxl_present_position, "comm" : dxl_comm_result, "error" : dxl_error, "ret" : False}
        else:
            return {"position" : self.dxl_present_position, "comm" : dxl_comm_result, "error" : dxl_error, "ret" : True}

    def controller(self) -> None:
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, DXL_ID, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        else:
            print("Dynamixel has been successfully connected")
        self.from_current_position : dict = self.get_current_position()
        self.dxl_present_position, dxl_comm_result, dxl_error = self.from_current_position["position"], self.from_current_position["comm"], self.from_current_position["error"]
        print(self.dxl_position_to_degree(dxl=self.dxl_present_position))
        while 1:

            if self.from_current_position["ret"] is False and self.from_current_position is not None:
                break 
            goal_position : int = self.degree_to_dxl_position(degree=float(input("")))     
            if (goal_position >= DXL_MINIMUM_POSITION_LIMIT and goal_position <= DXL_MAXIMUM_POSITION_LIMIT) is False:
                print("Goal position out of limit")
                break

            dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, DXL_ID, ADDR_PRO_GOAL_POSITION, goal_position) 
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            while 1:
                self.from_current_position = self.get_current_position()
                if self.from_current_position["ret"] is False:
                    break 
                self.dxl_present_position, dxl_comm_result, dxl_error = self.from_current_position["position"], self.from_current_position["comm"], self.from_current_position["error"]
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % self.packetHandler.getRxPacketError(dxl_error))
                print(f"[ID:{DXL_ID}] GoalPos:{self.dxl_position_to_degree(dxl=goal_position)}  PresPos:{self.dxl_position_to_degree(dxl=self.dxl_present_position)}") 
                if not abs(goal_position - self.dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD: 
                    break
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, DXL_ID, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        self.portHandler.closePort()

def main():
    dynamixel_driver : DynamixelDriver = DynamixelDriver()
    dynamixel_driver.controller()

if __name__ == "__main__":
    main()

















