from abc import abstractmethod, ABC
import subprocess

input = 'ls -l'
result = subprocess.run(input.split(), stderr=subprocess.PIPE, text=True, stdout=subprocess.PIPE)
print(result)
# print(result.stderr)

class Command(ABC):
    def __init__(self, input) -> None:        
        super().__init__()
        self.input = input

    @abstractmethod
    def execute(self) -> str:
        pass

class LinuxCommand(Command):
    def execute(self) -> str:
        result = subprocess.run(self.input.split(), stderr=subprocess.PIPE, text=True, stdout=subprocess.PIPE)
        # print(result)
        if result.returncode == 0:
            return result.stdout
        else:
            return result.stderr