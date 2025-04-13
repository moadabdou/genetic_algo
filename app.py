import random
import json

a_i = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!."
a = {char: idx for idx, char in enumerate(a_i)}
char_space = len(a) - 1

def word(length:int) -> list[int]:
    res:list[int] = []
    for _ in range(length):
        res.append( random.randint(0, char_space)) 
    return res

def word_to_arr(word:str) -> list[int]:
    return  [ a[letter]  for letter in word  ]


def generate_population(size:int, length:int) ->  list[int]:
    res:list[int] = [] 
    for _  in  range(size):
        res.append(word(length))
    return res

def translate(word:list[int]) -> str:
    res : str = "" 
    for letter in  word :  
        res +=  a_i[letter] 
    return res

def fitness_reference(target : str) -> int:
    res:list[int] = []
    for letter in target:
        res.append( max( char_space - a[letter], a[letter]))
    return res 

def  fitness(word:list[int],reference: list[int], target : str):
    res : int = 0
    for letter, tar, ref in zip(word, target, reference):
        res += ref - abs( letter - a[tar])
    return res

def cross_over(word1 : list[int], word2 :list[int])-> list[list]:
    p = random.randint(1,len(word1) - 1)
    return [ word1[:p]+word2[p:],  word2[:p]+word1[p:], p]

def mutation(word: list[int])->list[int]:
    mut = []
    for letter in word:
        new_letter = letter + int(random.normalvariate(0,1))
        if  new_letter > char_space :  new_letter = char_space 
        if  new_letter < 0 :  new_letter = 0
        mut.append(new_letter)
    return mut

def select( population : list[list],  reference : list[int], target:str)->list[int]:
    return random.choices(population, weights= [ fitness( _word , reference ,target) for _word in population ], k=2)


export = []


def eval(target: str, gen_size:int):

    population =  generate_population(gen_size, len(target))

    reference  = fitness_reference(target)
    tager_arr =  word_to_arr(target)
    gen = []
    for i  in population : 
        gen.append({
            "value" :  translate(i),
            "fitness" : fitness(i, reference, target),
            "parent" : False
        })
    export.append(gen)

    for i  in range(300):
        
        population = sorted(
            population,
            key=lambda x : fitness(x, reference, target),
            reverse=True
        )
        
        target_fitness = fitness(tager_arr, reference, target)
        current_fitness = fitness(population[0], reference, target)

        print( i,
              f"{current_fitness}/{target_fitness}: ", 
              translate(population[0]))
        
        if current_fitness ==  target_fitness : 
            print ("FOUND !")
            break

        next_gen:list[int] = population[0:2]
        parents = [
            {
                "value" : translate(g),
                "fitness" : fitness(g, reference, target),
                "parent" : True
            } for  g in next_gen
        ]
        gen = parents
        for _ in range(2, len(population), 2): 
            offspring_a, offspring_b,p =  cross_over(next_gen[0], next_gen[1])
            offspring_a_m =  mutation(offspring_a)
            offspring_b_m =  mutation(offspring_b)
            next_gen+= [offspring_a_m, offspring_b_m]
            gen += [{
                "p" : p,
                "pre_value" :  translate(offspring_a),
                "value" : translate(offspring_a_m),
                "fitness" : fitness(offspring_a_m, reference, target),
                "parent" : False
            },{
                "p" : p,
                "pre_value" :  translate(offspring_b),
                "value" : translate(offspring_b_m),
                "fitness" : fitness(offspring_b_m, reference, target),
                "parent" : False
            }]
        export.append(gen)
        population = next_gen


eval( "genome" , 20)      


with open("gens.json", "w") as out:
    out.write(json.dumps(export))
