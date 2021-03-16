import math
####################################################
class Vector:

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "({},{},{})".format(self.x, self.y, self.z)

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def magnitude(self):
        return math.sqrt(self.dot_product(self))

    def normalize(self):
        return self / self.magnitude()

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        assert not isinstance(other, Vector)
        return Vector(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        assert not isinstance(other, Vector)
        return Vector(self.x / other, self.y / other, self.z / other)

    def cosine(self, other, degree = 1):
        return (self.dot_product(other) * (1/(self.magnitude()*other.magnitude()))) ** degree

class Color(Vector):
    @classmethod
    def from_hex(cls,hexcolor = "#000000"):
        x = int(hexcolor[1:3], 16) / 255.0
        y = int(hexcolor[3:5], 16) / 255.0
        z = int(hexcolor[5:7], 16) / 255.0
        return cls(x, y, z)

class Image:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = [[None for _ in range(width)] for _ in range(height)]

    def set_pixel(self, x, y, col):
        self.pixels[y][x] = col

    def write_ppm(self, img_file):
        
        def to_byte(c):
            return round(max(min(c * 255, 255), 0))

        img_file.write("P3 {} {}\n255\n".format(self.width, self.height))
        for row in self.pixels:
            for color in row:
                img_file.write("{} {} {} ".format(to_byte(color.x), to_byte(color.y), to_byte(color.z)))
            img_file.write("\n")
    
class Point(Vector):
    pass

class Sphere:
    
    def __init__(self,center,radius,material):
        self.center = center
        self.radius = radius
        self.material = material
    
    def intersects(self,ray):
        sphere_to_ray = ray.origin - self.center
        a = 1
        b = 2 * ray.direction.dot_product(sphere_to_ray)
        c = sphere_to_ray.dot_product(sphere_to_ray) - self.radius * self.radius
        discriminant = b*b - 4*a*c

        if discriminant >= 0:
            dist = (-b - math.sqrt(discriminant)) / 2
            if dist > 0:
                return dist
        return None

    def normal(self, surface_point):
        return (surface_point - self.center).normalize() 

class Ray:

    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction.normalize()

class Scene:

    def __init__(self, camera, objects, lights, width, height):
        self.camera = camera
        self.objects = objects
        self.lights = lights
        self.width = width
        self.height = height

class RenderEngine:
    
    MAX_DEPTH = 5
    DELTA = 0.0001

    def render(self, scene):
        width = scene.width
        height = scene.height
        aspect_ratio = float(width) / height
        
        x0 = -1.0
        x1 = +1.0
        xstep = (x1 - x0) / (width - 1)
        
        y0 = -1.0 / aspect_ratio
        y1 = +1.0 / aspect_ratio
        ystep = (y1 - y0) / (height - 1)

        camera = scene.camera
        pixels = Image(width,height)

        for j in range(height):
            y = y0 + ystep * j
            for i  in range(width):
                x = x0 + xstep * i
                ray = Ray(camera, Point(x,y) - camera)
                pixels.set_pixel(i, j, self.ray_trace(ray, scene))
            print("{:3.0f}%".format(float(j)/float(height)*100), end="\r")
        return pixels

    def ray_trace(self, ray, scene, depth = 0):

        def reflected_light(A,B):
            return B * B.dot_product(A) * 2 - A

        color = Color(0.0,0.0,0.0)
        distance_hit, obj_hit = self.find_nearest(ray, scene)
        if obj_hit is not None:
            
            r = obj_hit.material.reflection
            hit_position = ray.origin + ray.direction * distance_hit
            hit_normal = obj_hit.normal(hit_position)
            color += self.color_at(obj_hit, hit_position, hit_normal, scene)
            if (depth >= 3) or (r <= 0):
                return color

            new_ray_position = hit_position + hit_normal * self.DELTA
            new_ray_direction = ray.direction - 2 * ray.direction.dot_product(hit_normal) * hit_normal
            new_ray = Ray(new_ray_position, new_ray_direction)

            R = reflected_light(new_ray_direction * -1.0, obj_hit.normal(hit_position))
            eps1 = 0.1
            splits = [Vector(R.x + eps1, R.y, R.z), Vector(R.x - eps1, R.y, R.z), Vector(R.x, R.y + eps1, R.z), Vector(R.x, R.y - eps1, R.z)]
            cosines = [(R - hit_position).cosine(splits[0] - hit_position, 100), (R - hit_position).cosine(splits[1] - hit_position, 100), (R - hit_position).cosine(splits[2] - hit_position, 100)]
            r_col = (self.ray_trace(new_ray, scene, depth + 1) + self.ray_trace(new_ray, scene, depth + 1)*cosines[0] + self.ray_trace(new_ray, scene, depth + 1)*cosines[1] + self.ray_trace(new_ray, scene, depth + 1)*cosines[2]) * (1/(1+sum(cosines)))

            return color * (1 - r) + r_col * r
        return color

    def find_nearest(self, ray, scene):
        dist_min = None
        obj_hit = None
        for obj in scene.objects:
            dist = obj.intersects(ray)
            if dist is not None and (obj_hit is None or dist < dist_min):
                dist_min = dist
                obj_hit = obj
        return (dist_min, obj_hit)
        
    def color_at(self, obj_hit, hit_pos, normal, scene):
        material = obj_hit.material
        obj_color = material.color_at(hit_pos)
        to_camera = scene.camera - hit_pos
        s = 50
        color = material.ambient * Color.from_hex("#000000")
        
        for light in scene.lights:

            shadow_t, shadow = self.find_nearest(Ray(hit_pos, light.position - hit_pos),scene)
            if shadow != None:
                continue

            to_light = Ray(hit_pos, light.position - hit_pos)
            color += obj_color * material.diffuse * max(normal.dot_product(to_light.direction), 0)

            middle_vector = (to_light.direction + to_camera).normalize()
            color += light.color * material.specular * max(normal.dot_product(middle_vector), 0) ** s
        return color

class Light:

    def __init__(self, position, color = Color.from_hex("#FFFFFF")):
        self.position = position
        self.color = color

class Material:
    
    def __init__(self, color=Color.from_hex("#FFFFFF"), ambient = 0.05, diffuse = 1.0, specular = 1.0, reflection = 0.5):
        self.color = color
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.reflection = reflection
    
    def color_at(self, position):
        return self.color

class ChessMaterial:
    
    def __init__(self, color1 = Color.from_hex("#FFFFFF"), color2 =Color.from_hex("#000000"), ambient = 0.05, diffuse = 1.0, specular = 1.0, reflection = 0.5):
        self.color1 = color1
        self.color2 = color2
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.reflection = reflection
    
    def color_at(self, position):
        if int((position.x + 5.0) * 3.0) % 2 == int(position.z * 3.0) % 2:
            return self.color1
        else:
            return self.color2

####################################################

def main():
    WIDTH = 900
    HEIGHT = 900

    camera = Vector(0.0, -0.35, -1.0)

    chessboard = Sphere(Point(0.0, 10000.5, 1.0), 10000.0, ChessMaterial(color1 = Color.from_hex("#420500"), color2 = Color.from_hex("#E6B87D"), ambient = 0.2, reflection = 0.2))
    
    red_b = Sphere(Point(2.0, -0.5, 2.5), 1.0, Material(Color.from_hex("#FF0000"), ambient=0.1))
    gre_b = Sphere(Point(-1.250, -0.5, 2.0), 1.0, Material(Color.from_hex("#00FF00"), diffuse= 0.1))
    blu_b = Sphere(Point(0.0, 0.0, 0.7), 0.5, Material(Color.from_hex("#0000FF"), specular=0.75))

    l = Light(Point(-0.6, -7.5, 1.5), Color.from_hex("#E6E6E6"))
    ll = Light(Point(-0.4, -7.5, -1.5), Color.from_hex("#E6E6E6"))
    lll = Light(Point(-0.4, -7.5, 1.5), Color.from_hex("#E6E6E6"))
    llll = Light(Point(-0.6, -7.5, -1.5), Color.from_hex("#E6E6E6"))
    objects = [chessboard, red_b, gre_b, blu_b]
    lights = [l, ll, lll, lll]

    scene = Scene(camera, objects, lights, WIDTH, HEIGHT) 
    engine = RenderEngine()
     
    image = engine.render(scene)

    with open("D:/teplpp/AAno_focus.ppm","w") as img_file:
        image.write_ppm(img_file)
    
    
    
    ### rezk
    
    focal_point = scene.objects[3].center.z
    eps = 0.05
    scamera0 = camera + Vector(0.0+eps, 0.350, -100.0)
    scamera1 = camera + Vector(0.0, 0.350+eps, -100.0)
    scamera2 = camera - Vector(0.0+eps, 0.350, -100.0)
    scamera3 = camera - Vector(0.0, 0.350+eps, -100.0)

    scameras = [scamera0, scamera1, scamera2, scamera3]
    simages = [Image(WIDTH,HEIGHT), Image(WIDTH,HEIGHT), Image(WIDTH,HEIGHT), Image(WIDTH,HEIGHT)]

    image2 = Image(WIDTH,HEIGHT)

################################
    w = scene.width
    h = scene.height
    aspect_ratio = float(w) / h
        
    x0 = -1.0
    x1 = +1.0
    xstep = (x1 - x0) / (w - 1)
        
    y0 = -1.0 / aspect_ratio
    y1 = +1.0 / aspect_ratio
    ystep = (y1 - y0) / (h - 1)
################################
    for count, img in enumerate(simages):
        scene.camera = scameras[count]
        for j in range(h):
            y = y0 + ystep * j
            for i  in range(w):
                x = x0 + xstep * i
                ray = Ray(scameras[count], (Point(x,y,4) * (focal_point / 2) - scameras[count]).normalize())
                col = engine.ray_trace(ray, scene)
                img.set_pixel(i, h - j - 1, col)
            print("{:3.0f}%".format(float(j)/float(h)*100), end="\r")
        simages[count] = img
    
    for j in range(h):
        for i  in range(w):
            image2.set_pixel(i, h - j - 1, (simages[0].pixels[j][i] + simages[1].pixels[j][i] + simages[2].pixels[j][i] + simages[3].pixels[j][i]) / 4)
            '''if image2.pixels[h - j - 1][i] is None:
                continue
            else:
                image2.set_pixel(i, h - j - 1, image2.pixels[j][i] * 0.25) '''

    
    
    with open("D:/teplpp/AAw_focus.ppm","w") as img_file:
        image2.write_ppm(img_file)
    

main()