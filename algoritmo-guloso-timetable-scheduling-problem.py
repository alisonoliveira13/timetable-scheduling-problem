import pandas as pd
from tabulate import tabulate

dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
horarios = ["Aula 1", "Aula 2", "Aula 3", "Aula 4"]

def coletar_entradas():
    turmas = {}
    num_turmas = int(input("Quantas turmas deseja adicionar? "))
    
    for _ in range(num_turmas):
        turma_nome = input("Nome da turma: ")
        turmas[turma_nome] = []
        num_disciplinas = int(input(f"Quantas disciplinas para a turma {turma_nome}? "))
        
        for _ in range(num_disciplinas):
            disciplina = input("Nome da disciplina: ")
            aulas = int(input(f"Quantidade de aulas para {disciplina}: "))
            professor = input(f"Professor para {disciplina}: ")
            turmas[turma_nome].append((disciplina, aulas, professor))
    
    return turmas

def criar_horario_alg_guloso(turmas):
    horario_turmas = {turma: pd.DataFrame("", index=horarios, columns=dias_semana) for turma in turmas.keys()}
    
    calendario_professores = {professor: {dia: [False]*4 for dia in dias_semana} for turma in turmas.values() for disciplina, aulas, professor in turma}
    
    contador_disciplinas = {turma: {dia: {} for dia in dias_semana} for turma in turmas.keys()}
    
    total_aulas = 0
    total_aulas_alocadas = 0
    
    for turma, disciplinas in turmas.items():
        for disciplina, aulas, professor in disciplinas:
            total_aulas += aulas
            alocadas = 0
            for dia in dias_semana:
                if alocadas >= aulas:
                    break
                for hora in range(0, 4, 2):  
                    if alocadas >= aulas:
                        break
                    if contador_disciplinas[turma][dia].get(disciplina, 0) >= 2:
                        continue
                    if horario_turmas[turma].iloc[hora, dias_semana.index(dia)] == "" and horario_turmas[turma].iloc[hora+1, dias_semana.index(dia)] == "":
                        if not calendario_professores[professor][dia][hora] and not calendario_professores[professor][dia][hora+1]:
                            horario_turmas[turma].iloc[hora, dias_semana.index(dia)] = f"{disciplina}\n{professor}"
                            horario_turmas[turma].iloc[hora+1, dias_semana.index(dia)] = f"{disciplina}\n{professor}"
                            alocadas += 2
                            total_aulas_alocadas += 2
                            calendario_professores[professor][dia][hora] = True
                            calendario_professores[professor][dia][hora+1] = True
                            contador_disciplinas[turma][dia][disciplina] = contador_disciplinas[turma][dia].get(disciplina, 0) + 2
                            
    return horario_turmas, total_aulas, total_aulas_alocadas


turmas = coletar_entradas()
horarios, total_aulas, total_aulas_alocadas = criar_horario_alg_guloso(turmas)


for turma, horario in horarios.items():
    print(f"\nTabela de Horários - {turma}\n")
    print(tabulate(horario, headers='keys', tablefmt='grid', showindex=True))


print(f"\nTotal de aulas solicitadas: {total_aulas}")
print(f"Total de aulas alocadas: {total_aulas_alocadas}")
print(f"Aulas não alocadas: {total_aulas - total_aulas_alocadas}")
