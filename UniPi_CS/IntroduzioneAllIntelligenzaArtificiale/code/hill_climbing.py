def hill_climbing(problem): """ Ricerca locale - Hill-climbing."""
  current = Node(problem.initial_state)
  while True:
    neighbors = [current.child_node(problem, action) for action in
    problem.actions(current.state)]
    if not neighbors: # se current non ha successori esci e restituisci current
      break
    # scegli il vicino con valore piu' alto (sulla funzione problem.value)
    neighbor = (sorted(neighbors,key = lambda x:problem.value(x), reverse = True))[0]
    if problem.value(neighbor) <= problem.value(current):
      break
    else:
      current = neighbor # (altrimenti, se vicino e’ migliore, continua)
  return current
