import simpy
import random
import statistics 


#se inicia el environment    
opspersec = 1/3
velocidadProce = 3
processes = 200
env = simpy.Environment() #ambiente de simulación
ram2 = simpy.Container(env,init=100,capacity = 100) #se define la ram como tipo container
cpu = simpy.Resource(env, capacity=2) #se define el cpu como tipo resource
waiting2 = simpy.Resource(env, capacity = 1)
random.seed(3435)
interval = 1
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
        self.tiempo_in = 0
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
            
           

    def ready(self):
        #Listo para correr, esperando a CPU
        print('%5.1f Proceso #%i admitido y listo para correr en CPU' % (env.now, self.nombre))
        with self.cpu.request() as cola:
            yield cola #Esperando para correr
            env.process(self.running())
            

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
        
            


    
def creator(env, total, interval, cpu, ram2, waiting2):
    for i in range(total):
        ins = random.randint(1, 10)
        ram = random.randint(1, 10)
        proc = Process(i, ram, ram2, cpu, waiting2, ins, env)
        #env.process(proc)
        time = random.expovariate(1 / interval)
        yield env.timeout(time)
       
        

#SIMULACION
#for i in range(processes):
    #ins = random.randint(1, 10)
    #ram = random.randint(1, 10)
    #c=Process(round(i), ram, ram2, cpu, waiting2, ins, env)
env.process(creator(env, processes, interval, cpu, ram2, waiting2))
env.run(until=10000)
stats()
