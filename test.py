class Circle:
    def __init__(self):
        self.radius = 10
        self.color = "red"
    def add_radius(self, radius):
        self.radius += radius
        return (self.radius)

C1 = Circle()
print(C1)
C1 = C1.add_radius(8)
print(type(C1))
#%%
sum((1,2))
# %%
