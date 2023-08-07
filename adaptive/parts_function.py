class PartsFunction:
    def funcA(values: list):
        return sum(values)
    
    def funcB(values: list):
        result = values[0]
        for i in range(1, len(values)):
            result -= values[i]
        
        return result
    
    def funcC(values: list):
        result = values[0]
        for i in range(1, len(values)):
            result *= values[i]

        return result
    
    def funcD(values: list):
        result = values[0]
        for i in range(1, len(values)):
            result /= values[i]

        return result    