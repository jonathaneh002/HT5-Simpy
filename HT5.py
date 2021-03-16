#se importan las librerias
import simpy
import random
import statistics 


#se definen las caracteristicas de la computadora
velocidadProce = 3
opspersec = 1/velocidadProce
processes = 25
env = simpy.Environment() #ambiente de simulación
ram2 = simpy.Container(env,init=100,capacity = 100) #se define la ram como tipo container
cpu = simpy.Resource(env, capacity=1) #se define el cpu como tipo resource
waiting2 = simpy.Resource(env, capacity = 1)
#se define la seed
random.seed(3435)
interval = 10
tiempo = []


#se crea la clase que tendra objetos de tipo proceso
class Process(object):
    def __init__(self, nombre, ram, ram2, cpu, waiting2, instrucciones,env):
        self.env=env
        self.nombre = round(nombre, 1)
        self.ram=ram
        self.ram2=ram2
        self.cpu = cpu
        self.waiting2=waiting2
        self.instrucciones=instrucciones
        self.action = env.process(self.new())

    #estado new
    def new(self):
        self.tiempo_in = env.now
        #proceso llega al OS y espera a que se le asigne ram
        with self.ram2.get(self.ram) as asignRam:
            if(self.ram <= self.ram2.level):
                print('%5.1f al Proceso #%i se le asigna %i de RAM y queda %i disponible' % (env.now, self.nombre, self.ram, self.ram2.level))
                yield asignRam #se le asigna la ram solicitada
                env.process(self.ready())
            else:
                print('%5.1f Proceso #%i en cola esperando RAM' % (env.now, self.nombre))
            
           
    #estado de ready en el que esta listo para correr y espera al CPU
    def ready(self):
        #Listo para correr, esperando a CPU
        print('%5.1f Proceso #%i admitido y listo para correr en CPU' % (env.now, self.nombre))
        with self.cpu.request() as cola:
            yield cola #Esperando para correr
            env.process(self.running())
            

    #estado en el que el procesador ejecuta las instrucciones
    def running(self):
        #se solicita entrar al cpu
        with self.cpu.request() as req:
            yield req
            
            #se comienza a ejecutar las operaciones de 1 a 10 disminuyendolo en 3
            print('%5.1f El Proceso #%i, con %i instrucciones, se comenzó a ejecutar en el cpu en %i' % (env.now, self.nombre, self.instrucciones, env.now))
            for i in range(velocidadProce):
                if(self.instrucciones > 0):
                    self.instrucciones-=1
                    yield(env.timeout(opspersec))
      
        #si el proceso es de menos de 3 operaciones o ya finalizo entonces
        #se interrumpe y se envia a terminated donde se retorna la memoria ram
        if(self.instrucciones == 0):
            env.process(self.terminated())

        else:
            continuar=random.randint(1,2)
            print('%5.1f El Proceso #%i ahora le quedan %i instrucciones y le toco el numero %g' % (env.now, self.nombre, self.instrucciones,continuar))
            if continuar == 1:
                env.process(self.waiting())
                print("%5.1f Se envió el Proceso #%i a la cola de Waiting en %5.1f" %(env.now, self.nombre, env.now))
            else:
                env.process(self.ready())
                print("%5.1f Se envió el Proceso #%i a la cola de Ready en %5.1f" %(env.now, self.nombre, env.now))
        
            
        
    #estado en donde espera y hace operaciones de I/O regresando a ready
    def waiting(self):
        with self.waiting2.request() as waiting_queue:
            yield waiting_queue
            print('%5.1f Proceso #%i Haciendo operaciones I/O en %g' %(env.now, self.nombre, env.now))
            yield env.timeout(random.randint(1, 10))#Hace operaciones por x tiempo
            print('%5.1f Proceso #%i Termino operaciones I/O en %g' %(env.now, self.nombre, env.now))
            env.process(self.ready())
        
        
        
    #estado donde se ha finalizado el proceso
    def terminated(self):
        with self.ram2.put(self.ram) as asignRam:
            yield asignRam #se le devuelve la ram utilizada
            print('%5.1f Proceso #%i Instrucciones terminadas en %5.1f memoria actual %s' %(env.now, self.nombre, env.now,self.ram2.level))
        tiempo.append(env.now - self.tiempo_in)

    
#metodo que genera los procesos en el intervalo que se le indica
def creator(env, total, interval, cpu, ram2, waiting2):
    for i in range(total):
        ins = random.randint(1, 10)
        ram = random.randint(1, 10)
        proc = Process(i, ram, ram2, cpu, waiting2, ins, env)
        time = random.expovariate(1.0/ interval)
        yield env.timeout(time)
       
        

#SIMULACION
env.process(creator(env, processes, interval, cpu, ram2, waiting2))
env.run(until=500)
