from typing import Optional
from pydantic import BaseModel, Field

class HardwareConfigResponse(BaseModel):
    main_port: Optional[str] = Field(default=None, description="Port for the main microcontroller (e.g. U2D2 or shared MCU)")
    independent_data_acquisition: bool = Field(default=False, description="True if a separate port is used for data acquisition")
    data_port: Optional[str] = Field(default=None, description="Port for independent data acquisition")
    sensor_type: str = Field(default="umyo", description="Type of sensor being used (umyo, gravitys)")
    motor_type: str = Field(default="dynamixels", description="Type of motors being used (dynamixels, servos)")

class HardwareConfigUpdate(BaseModel):
    main_port: Optional[str] = None
    independent_data_acquisition: bool = False
    data_port: Optional[str] = None
    sensor_type: str = "umyo"
    motor_type: str = "dynamixels"
