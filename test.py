class A(object):
    inner_var = 0

    @classmethod
    def setInnerVar(cls, value):
        cls.inner_var = value

    @classmethod
    def echoInnerVar(cls):
        print cls.inner_var


class B(A):
    pass


A.setInnerVar(10)
B.setInnerVar(20)

A.echoInnerVar()
B.echoInnerVar()
