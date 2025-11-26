from datetime import datetime


class Logger:
    def __init__(self) -> None:
        self.log_time = datetime.now()

    def err(self, component_name, message):
        self.component_name = component_name
        self.message = message
        print(f"[{self.log_time}] [ERROR] - {self.component_name} - {self.message}")
        
    def log(self, component_name, message):
        self.component_name = component_name
        self.message = message
        print(f"[{self.log_time}] [GAME LOG] - {self.component_name} - {self.message}")
        
    
