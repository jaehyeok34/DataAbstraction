class PartsFunction:
    def funcA(values: list) -> int:
        return sum(values)
    
    def funcB(values: list) -> int:
        result = values[0]
        for i in range(1, len(values)):
            result -= values[i]
        
        return result
    
    def funcC(values: list) -> int:
        result = values[0]
        for i in range(1, len(values)):
            result *= values[i]

        return result
    
    def funcD(values: list) -> int | float:
        result = values[0]
        for i in range(1, len(values)):
            result /= values[i]

        return result    