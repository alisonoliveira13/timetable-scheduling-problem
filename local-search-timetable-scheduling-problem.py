import copy
import random
import pandas as pd
from tabulate import tabulate

dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
horarios = ["Aula 1", "Aula 2", "Aula 3", "Aula 4"]

def coletar_entradas():
    semestres = {}
    num_semestres = int(input("Quantos semestres deseja adicionar? "))
    for _ in range(num_semestres):
        semestre_nome = input("Nome do semestre: ")
        semestres[semestre_nome] = []
        num_disciplinas = int(input(f"Quantas disciplinas para o semestre {semestre_nome}? "))
        for _ in range(num_disciplinas):
            disciplina = input("Nome da disciplina: ")
            aulas = int(input(f"Quantidade de aulas para {disciplina}: "))
            professor = input(f"Professor para {disciplina}: ")
            semestres[semestre_nome].append((disciplina, aulas, professor))
    return semestres

def criar_horario_alg_guloso(semestres):
    horario_semestres = {semestre: pd.DataFrame("", index=horarios, columns=dias_semana)
                         for semestre in semestres.keys()}
    calendario_professores = {
        professor: {dia: [False]*4 for dia in dias_semana}
        for semestre in semestres.values() for disciplina, aulas, professor in semestre
    }
    contador_disciplinas = {semestre: {dia: {} for dia in dias_semana}
                            for semestre in semestres.keys()}
    total_aulas = 0
    total_aulas_alocadas = 0
    for semestre in semestres:
        for disciplina, aulas, professor in semestres[semestre]:
            total_aulas += aulas
            alocadas = 0
            for dia in dias_semana:
                if alocadas >= aulas:
                    break
                col = dias_semana.index(dia)
                for block_index in [0, 2]:
                    if alocadas >= aulas:
                        break
                    if contador_disciplinas[semestre][dia].get(disciplina, 0) >= 2:
                        continue
                    if (horario_semestres[semestre].iloc[block_index, col] == "" and
                        horario_semestres[semestre].iloc[block_index+1, col] == ""):
                        if (not calendario_professores[professor][dia][block_index] and
                            not calendario_professores[professor][dia][block_index+1]):
                            horario_semestres[semestre].iloc[block_index, col] = f"{disciplina}\n{professor}"
                            horario_semestres[semestre].iloc[block_index+1, col] = f"{disciplina}\n{professor}"
                            alocadas += 2
                            total_aulas_alocadas += 2
                            calendario_professores[professor][dia][block_index] = True
                            calendario_professores[professor][dia][block_index+1] = True
                            contador_disciplinas[semestre][dia][disciplina] = \
                                contador_disciplinas[semestre][dia].get(disciplina, 0) + 2
    return horario_semestres, total_aulas, total_aulas_alocadas, calendario_professores, contador_disciplinas

def criar_horario_randomico(semestres):
    horario_semestres = {semestre: pd.DataFrame("", index=horarios, columns=dias_semana)
                         for semestre in semestres.keys()}
    calendario_professores = {
        professor: {dia: [False]*4 for dia in dias_semana}
        for semestre in semestres.keys() for disciplina, aulas, professor in semestres[semestre]
    }
    contador_disciplinas = {semestre: {dia: {} for dia in dias_semana}
                            for semestre in semestres.keys()}
    total_aulas = 0
    total_aulas_alocadas = 0
    for semestre in semestres:
        for disciplina, aulas, professor in semestres[semestre]:
            total_aulas += aulas
            alocadas = 0
            while alocadas < aulas:
                candidate_slots = []
                dias_disponiveis = dias_semana[:]  # copia da lista
                random.shuffle(dias_disponiveis)
                for dia in dias_disponiveis:
                    if contador_disciplinas[semestre][dia].get(disciplina, 0) >= 2:
                        continue
                    col = dias_semana.index(dia)
                    blocos = [0, 2]
                    random.shuffle(blocos)
                    for block_index in blocos:
                        if (horario_semestres[semestre].iloc[block_index, col] == "" and
                            horario_semestres[semestre].iloc[block_index+1, col] == ""):
                            if (not calendario_professores[professor][dia][block_index] and 
                                not calendario_professores[professor][dia][block_index+1]):
                                candidate_slots.append((dia, block_index))
                if candidate_slots:
                    chosen_day, chosen_block = random.choice(candidate_slots)
                    col = dias_semana.index(chosen_day)
                    horario_semestres[semestre].iloc[chosen_block, col] = f"{disciplina}\n{professor}"
                    horario_semestres[semestre].iloc[chosen_block+1, col] = f"{disciplina}\n{professor}"
                    alocadas += 2
                    total_aulas_alocadas += 2
                    calendario_professores[professor][chosen_day][chosen_block] = True
                    calendario_professores[professor][chosen_day][chosen_block+1] = True
                    contador_disciplinas[semestre][chosen_day][disciplina] = contador_disciplinas[semestre][chosen_day].get(disciplina, 0) + 2
                else:
                    break
    return horario_semestres, total_aulas, total_aulas_alocadas, calendario_professores, contador_disciplinas

def compute_allocations(horario_semestres, semestres):
    allocations = {}
    for semestre, disciplinas in semestres.items():
        allocations[semestre] = {}
        for disc, required, prof in disciplinas:
            allocations[semestre][disc] = 0
        for dia in dias_semana:
            for hora in horarios:
                celula = horario_semestres[semestre].loc[hora, dia]
                if celula != "":
                    disc = celula.split("\n")[0]
                    allocations[semestre][disc] += 1
        for disc in allocations[semestre]:
            allocations[semestre][disc] //= 2
    return allocations

def compute_cost(allocations, semestres):
    cost = 0
    for semestre, disciplinas in semestres.items():
        for disc, required, prof in disciplinas:
            allocated = allocations[semestre].get(disc, 0)
            needed = (required // 2) - allocated
            if needed > 0:
                cost += needed
    return cost

def try_relocation_moves(solution, semestres, current_cost):
    horario_semestres, total_aulas, total_aulas_alocadas, calendario_professores, contador_disciplinas = solution
    for semestre in sorted(horario_semestres.keys()):
        for day_from in dias_semana:
            col_from = dias_semana.index(day_from)
            for block_index in [0, 2]:
                if horario_semestres[semestre].iloc[block_index, col_from] != "":
                    conteudo = horario_semestres[semestre].iloc[block_index, col_from]
                    disciplina, professor = conteudo.split("\n")
                    for day_to in dias_semana:
                        if day_to == day_from:
                            continue
                        col_to = dias_semana.index(day_to)
                        if (horario_semestres[semestre].iloc[block_index, col_to] != "" or
                            horario_semestres[semestre].iloc[block_index+1, col_to] != ""):
                            continue
                        if contador_disciplinas[semestre][day_to].get(disciplina, 0) >= 2:
                            continue
                        if (calendario_professores[professor][day_to][block_index] or
                            calendario_professores[professor][day_to][block_index+1]):
                            continue
                        candidate = copy.deepcopy(solution)
                        candidate_horario = candidate[0]
                        candidate_calendario = candidate[3]
                        candidate_contador = candidate[4]
                        candidate_horario[semestre].iloc[block_index, col_from] = ""
                        candidate_horario[semestre].iloc[block_index+1, col_from] = ""
                        candidate_contador[semestre][day_from][disciplina] -= 2
                        candidate_calendario[professor][day_from][block_index] = False
                        candidate_calendario[professor][day_from][block_index+1] = False
                        candidate_horario[semestre].iloc[block_index, col_to] = f"{disciplina}\n{professor}"
                        candidate_horario[semestre].iloc[block_index+1, col_to] = f"{disciplina}\n{professor}"
                        candidate_contador[semestre][day_to][disciplina] = candidate_contador[semestre][day_to].get(disciplina, 0) + 2
                        candidate_calendario[professor][day_to][block_index] = True
                        candidate_calendario[professor][day_to][block_index+1] = True
                        new_alloc = compute_allocations(candidate_horario, semestres)
                        new_cost = compute_cost(new_alloc, semestres)
                        if new_cost < current_cost:
                            return candidate, new_cost
    return None, current_cost

def try_insertion_moves(solution, semestres, current_cost):
    horario_semestres, total_aulas, total_aulas_alocadas, calendario_professores, contador_disciplinas = solution
    allocations = compute_allocations(horario_semestres, semestres)
    for semestre in sorted(horario_semestres.keys()):
        for disc, required, prof in semestres[semestre]:
            allocated = allocations[semestre].get(disc, 0)
            if allocated < (required // 2):
                for day in dias_semana:
                    if contador_disciplinas[semestre][day].get(disc, 0) >= 2:
                        continue
                    col = dias_semana.index(day)
                    for block_index in [0, 2]:
                        if (horario_semestres[semestre].iloc[block_index, col] == "" and
                            horario_semestres[semestre].iloc[block_index+1, col] == ""):
                            if (calendario_professores[prof][day][block_index] or
                                calendario_professores[prof][day][block_index+1]):
                                continue
                            candidate = copy.deepcopy(solution)
                            candidate_horario = candidate[0]
                            candidate_calendario = candidate[3]
                            candidate_contador = candidate[4]
                            candidate_horario[semestre].iloc[block_index, col] = f"{disc}\n{prof}"
                            candidate_horario[semestre].iloc[block_index+1, col] = f"{disc}\n{prof}"
                            candidate_contador[semestre][day][disc] = candidate_contador[semestre][day].get(disc, 0) + 2
                            candidate_calendario[prof][day][block_index] = True
                            candidate_calendario[prof][day][block_index+1] = True
                            new_alloc = compute_allocations(candidate_horario, semestres)
                            new_cost = compute_cost(new_alloc, semestres)
                            if new_cost < current_cost:
                                return candidate, new_cost
    return None, current_cost

def local_search_deterministic(solution, semestres, max_iter=1000):
    current_solution = solution
    allocations = compute_allocations(current_solution[0], semestres)
    current_cost = compute_cost(allocations, semestres)
    iter_count = 0
    improved = True
    while improved and iter_count < max_iter:
        improved = False
        candidate, candidate_cost = try_relocation_moves(current_solution, semestres, current_cost)
        if candidate is not None and candidate_cost < current_cost:
            current_solution = candidate
            current_cost = candidate_cost
            improved = True
        else:
            candidate, candidate_cost = try_insertion_moves(current_solution, semestres, current_cost)
            if candidate is not None and candidate_cost < current_cost:
                current_solution = candidate
                current_cost = candidate_cost
                improved = True
        iter_count += 1
    return current_solution

def testar_busca_local_iteracoes(semestres, num_iteracoes=50, max_iter_busca=1000):
    # Primeira iteração: utiliza a solução gulosa
    sol_inicial = criar_horario_alg_guloso(semestres)
    sol_local = local_search_deterministic(sol_inicial, semestres, max_iter_busca)
    allocations_local = compute_allocations(sol_local[0], semestres)
    best_cost = compute_cost(allocations_local, semestres)
    best_solution = sol_local
    print(f"Iteração 1: Custo = {best_cost}")
    
    for i in range(1, num_iteracoes):
        sol_random = criar_horario_randomico(semestres)
        sol_local = local_search_deterministic(sol_random, semestres, max_iter_busca)
        allocations_local = compute_allocations(sol_local[0], semestres)
        cost_local = compute_cost(allocations_local, semestres)
        print(f"Iteração {i+1}: Custo = {cost_local}")
        if cost_local < best_cost:
            best_cost = cost_local
            best_solution = sol_local
    return best_solution, best_cost

if __name__ == "__main__":
    print("=== Coleta de Instâncias ===")
    semestres = coletar_entradas()
    
    sol_guloso = criar_horario_alg_guloso(semestres)
    allocations_guloso = compute_allocations(sol_guloso[0], semestres)
    cost_guloso = compute_cost(allocations_guloso, semestres)
    
    print("\n--- Solução Determinística (Guloso) ---")
    for semestre, horario in sol_guloso[0].items():
        print(f"\nTabela de Horários - {semestre}")
        print(tabulate(horario, headers="keys", tablefmt="grid", showindex=True))
    print(f"\nCusto (blocos faltantes) da solução gulosa: {cost_guloso}")
    print(f"Total de aulas solicitadas: {sol_guloso[1]}")
    print(f"Total de aulas alocadas: {sol_guloso[2]}")
    
    print("\n=== Testando Busca Local com Novas Soluções Aleatórias (50 iterações) ===")
    best_solution, best_cost = testar_busca_local_iteracoes(semestres, num_iteracoes=50, max_iter_busca=1000)
    
    horarios_final, total_aulas_final, total_aulas_alocadas_final, _, _ = best_solution
    allocations_final = compute_allocations(horarios_final, semestres)
    
    print("\n--- Melhor Solução Encontrada (após Busca Local) ---")
    for semestre, horario in horarios_final.items():
        print(f"\nTabela de Horários - {semestre}")
        print(tabulate(horario, headers="keys", tablefmt="grid", showindex=True))
    print("\nAlocações finais por disciplina:")
    for semestre, alloc in allocations_final.items():
        print(f"{semestre}: {alloc}")
    print(f"\nCusto final (blocos faltantes): {best_cost}")
    print(f"Total de aulas solicitadas: {total_aulas_final}")
    print(f"Total de aulas alocadas: {total_aulas_alocadas_final}")
