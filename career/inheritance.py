

class Database:
    """Tokenize text"""
    def __init__(self):
        print('Start Database.__init__()')
        self.db = 'Database'
        print('End Database.__init__()')

class A(Database):
    """Count words in text"""
    def __init__(self):
        print('Start A.__init__()')
        super().__init__()
        self.a = f"class-A | self.a : inherit from {self.db}"
        print('End A.__init__()')

class B:
    # b = 'bb'
    """Find unique words in text"""
    def __init__(self):
        print('Start B.__init__()')
        super(B, self).__init__()
        self.b = 'class-B | self.b : not inherited.'
        print('End B.__init__()')

class C:

    def __init__(self):
        print('Start C.__init__()')
        super(C, self).__init__()
        self.c = 'class-C | self.c : not inherited.'
        print('End C.__init__()')


class D(B,C,A):

    def __init__(self):
        print('Start D.__init__()')
        super().__init__()
        print('End D.__init__()')

D.__mro__
td = D()
td.db
td.a
td.b
td.c

class A(object):

    def __init__(self, *args, **kwargs):
        super(A, self).__init__(*args, **kwargs)
        self.number = kwargs['number']

    def helloA(self):
        return self.number

class B(object):

    def __init__(self, *args, **kwargs):
        super(B, self).__init__()
        self.message = kwargs['message']

    def helloB(self):
        return self.message

class C(A,B):

    def __init__(self, *args, **kwargs):
        # Notice: only one call to super... due to mro
        # super(C, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def helloC(self):
        print(f"Calling A: {self.helloA()}")
        print(f"Calling B: {self.helloB()  }")

c = C(number=42, message="Joe")
c.helloC()
