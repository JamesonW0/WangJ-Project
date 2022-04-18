class Stuff:
    def __init__(self):
        self.a = 100

    def func_1(self):
        def fun():
            self.a = 0
        fun()

    def get_a(self):
        return self.a


x = Stuff()
print(x.get_a())
x.func_1()
print(x.get_a())
