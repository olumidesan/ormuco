

# Python 3.6+

class InvalidComparisonError(Exception):
    """
    Version string exception triggered when a version string (an instance of Version String class)
    is being compared with an object thats not also a version string

    """

    pass


class VersionString(str):
    """
       This class allows for instantiation and comparisons between version strings.
       It also assumes that version string "1.1.2" is not equal to "1.1.2.0"; it 
       assumes the former precedes (and is therefore less than) the latter.
       Instances of this class *can* only be compared with other instances of
       this class

    """

    def __init__(self, v_str):
        
        # Validate the version string upon initial construction.
        try:
            [int(i) for i in v_str.split(".")]
        except ValueError:
            print("Version Strings must be period delimited strings of integers.")
            raise

        self.v_str = v_str


    @staticmethod
    def validate_vstr(v_str):

        # Validate the version string to ensure it is an instance of this class
        if not isinstance(v_str, VersionString):
            raise InvalidComparisonError("Version strings can only be compared with other version strings")


    def __eq__(self, v_str2):

        # Only instances of version strings can be compared
        self.validate_vstr(v_str2)

        _v_str = self.v_str.split(".")
        _v_str2 = v_str2.split(".")
        
        len_v_str = len(_v_str)
        len_v_str2 = len(_v_str2)

        # If their lengths don't match to begin with, then they surely
        # cannot be equal, using the stated assumption in the class' 
        # docstring: i.e. "1.2.6" != "1.2.6.0". "1.2.6" is lesser
        if len_v_str !=  len_v_str2:
            return False

        for i,j in zip(_v_str, _v_str2):
            if int(i) != int(j):
                return False
        
        return True


    def __ne__(self, v_str2):
        
        self.validate_vstr(v_str2)

        # return the inverse of calling self.__eq__()
        return not self.v_str.__eq__(v_str2)


    def __lt__(self, v_str2):

        self.validate_vstr(v_str2)

        # Confirm if the values being checked are not 
        # equal, to begin with. (Just in case)
        if self.v_str.__eq__(v_str2):
            return False

        _v_str = self.v_str.split(".")
        _v_str2 = v_str2.split(".")
        
        len_v_str = len(_v_str)
        len_v_str2 = len(_v_str2)

        for i, j in zip(_v_str, _v_str2):
            _i, _j = int(i), int(j)
            if _i < _j:
                return True

            elif _i > _j:
                return False

            elif _i == _j:
                if _v_str.index(i) == (len_v_str - 1):
                    return True

                elif _v_str2.index(j) == (len_v_str2 - 1):
                    return False


    def __gt__(self, v_str2):
        
        self.validate_vstr(v_str2)
        
        if self.v_str.__eq__(v_str2):
            return False
            
        return not self.__lt__(v_str2)

