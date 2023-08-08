class PartsFunction:
    def add(values: list) -> int:
        return sum(values)
    
    def sub(values: list) -> int:
        result = values[0]
        for i in range(1, len(values)):
            result -= values[i]
        
        return result
    
    def mul(values: list) -> int:
        result = values[0]
        for i in range(1, len(values)):
            result *= values[i]

        return result
    
    def div(values: list) -> int | float:
        result = values[0]
        for i in range(1, len(values)):
            result /= values[i]

        return result    