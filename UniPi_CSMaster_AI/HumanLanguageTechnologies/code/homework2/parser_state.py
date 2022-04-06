
class ParserState():

    # map simple transition names to their id
    tr2id = {'S': 0, 'LA': 2, 'RA': 1}

    def __init__(self, stack=[], buffer=[], arcs=[]):
        """Initializes this parser state.

        @param stack (list of str): initial stack.
        @param buffer (list of str): initial buffer.
        @param arcs (list of triples (head, dependent, deprel)): initial dependencies.
        """

        ### YOUR CODE HERE (3 Lines)
        ### Your code should initialize the following fields:
        ###     self.stack: The current stack represented as a list with the
        ###                 top of the stack as the last element of the list.
        ###     self.buffer: The current buffer represented as a list with the
        ###                  first item on the buffer as the first item of the list
        ###     self.arcs: The list of dependencies produced so far. Represented as a list of
        ###             tuples where each tuple is of the form (head, dependent).
        ###             Order for this list doesn't matter.
        ###
        ### Note: The root token should be represented with the string "ROOT"
        ### Note: If you need to use the sentence object to initialize anything, make sure to not directly 
        ###       reference the sentence object.  That is, remember to NOT modify the sentence object. 

        self.stack = list(stack) # copy to avoid clobbering
        self.buffer = list(buffer)
        self.arcs = arcs

        ### END YOUR CODE


    def step(self, transition):
        """Performs a single parse step by applying the given transition to this partial parse


        @param transition (int): An integer encoding a transition:
            0: Shift
            2 * deprel: LEFT-ARC with label deprel
            2 * deprel + 1: RIGHT-ARC with label deprel
        @return: True if the transition was feasible.
        """
        ### YOUR CODE HERE (~10-12 Lines)
        ### TODO:
        ###     Implement a single parsing step, i.e. the logic for the following transitions:
        ###         1. Shift
        ###         2. Left Arc
        ###         3. Right Arc

        if transition == 0:  # Shift
            if not self.buffer:
                return False
            self.stack.append(self.buffer[0])
            self.buffer.pop(0)
        elif transition % 2: # RIGHT-ARC
            if len(self.stack) < 2:
                return False
            deprel = (transition -1) // 2
            self.arcs.append((self.stack[-2], self.stack[-1], deprel))
            self.stack.pop()
        else:                # LEFT-ARC
            if len(self.stack) < 3: # no LEFT-ARC to ROOT
                return False
            deprel = transition // 2
            self.arcs.append((self.stack[-1], self.stack[-2], deprel))
            self.stack.pop(-2)
        return True

        ### END YOUR CODE

    def parse(self, transitions):
        """Applies the provided transitions to this ParserState

        @param transitions (list of str): The list of transitions in the order they should be applied

        @return arcs (list of string tuples): The list of arcs produced when
                                                        parsing the sentence. Represented as a list of
                                                        tuples where each tuple is of the form (head, dependent).
        """
        for transition in transitions:
            self.step(self.tr2id[transition])
        return self.arcs


    def extract_features(self, parser):
        """
        Feature representation of current state.
        Features are:
         - form, pos for these tokens:
           - top 3 frome stack, first 3 from buffer
           - the following children of top 2 stack tokens:
               lc[0], rc[0], lc[1], rc[1], llc[0], rrc[0]
         - deprels of the following children of the top 2 stack tokens:
             lc[0], rc[0], lc[1], rc[1], llc[0], rrc[0]
        @return: a triple (list of form ids, list of POS ids, list of DEPREL ids).
        """

        def get_lc(tok):
            """Left children"""
            return sorted([arc[1] for arc in self.arcs if arc[0] == tok and arc[1].id < tok.id],
                          key=lambda x: x.id)

        def get_rc(tok):
            """Right children"""
            return sorted([arc[1] for arc in self.arcs if arc[0] == tok and arc[1].id > tok.id],
                          key=lambda x: x.id,
                          reverse=True)

        def get_h(tok):
            """Head of token from arcs created so far."""
            return next((arc[0].deprel for arc in self.arcs
                         if arc[1] == tok),
                        parser.DEPREL_PAD)

        # last 3 words from stack (PAD if missing)
        features = [parser.PAD] * (3 - len(self.stack)) + [x.form for x in self.stack[-3:]]
        # first 3 words from buffer (PAD if missing)
        features += [x.form for x in self.buffer[:3]] + [parser.PAD] * (3 - len(self.buffer))
        # last 3 POS from stack
        p_features = [parser.POS_PAD] * (3 - len(self.stack)) + [x.pos for x in self.stack[-3:]]
        # firt 3 POS from buffer
        p_features += [x.pos for x in self.buffer[:3]] + [parser.POS_PAD] * (3 - len(self.buffer))
        # DEPREL features (none from token on the stack, hence padding,
        # consider only those created by parser) 
        l_features = [parser.DEPREL_PAD] * 6

        pad_f = len(features)
        pad_pf = len(p_features)
        pad_lf = len(l_features)

        for i in range(2): # the two top words on the stack
            if i < len(self.stack):
                k = self.stack[-i-1]
                lc = get_lc(k)
                rc = get_rc(k)
                llc = get_lc(lc[0]) if len(lc) > 0 else []
                rrc = get_rc(rc[0]) if len(rc) > 0 else []

                # form features of top 2 stack children
                features.append(lc[0].form if len(lc) > 0 else parser.PAD)
                features.append(rc[0].form if len(rc) > 0 else parser.PAD)
                features.append(lc[1].form if len(lc) > 1 else parser.PAD)
                features.append(rc[1].form if len(rc) > 1 else parser.PAD)
                features.append(llc[0].form if len(llc) > 0 else parser.PAD)
                features.append(rrc[0].form if len(rrc) > 0 else parser.PAD)

                # POS features of top 2 stack children
                p_features.append(lc[0].pos if len(lc) > 0 else parser.POS_PAD)
                p_features.append(rc[0].pos if len(rc) > 0 else parser.POS_PAD)
                p_features.append(lc[1].pos if len(lc) > 1 else parser.POS_PAD)
                p_features.append(rc[1].pos if len(rc) > 1 else parser.POS_PAD)
                p_features.append(llc[0].pos if len(llc) > 0 else parser.POS_PAD)
                p_features.append(rrc[0].pos if len(rrc) > 0 else parser.POS_PAD)

                # DEPREL features of top 2 stack children
                # Consider onluy arcs created by parser, not gold ones.
                l_features.append(get_h(lc[0]) if len(lc) > 0 else parser.DEPREL_PAD)
                l_features.append(get_h(rc[0]) if len(rc) > 0 else parser.DEPREL_PAD)
                l_features.append(get_h(lc[1]) if len(lc) > 1 else parser.DEPREL_PAD)
                l_features.append(get_h(rc[1]) if len(rc) > 1 else parser.DEPREL_PAD)
                l_features.append(get_h(llc[0]) if len(llc) > 0 else parser.DEPREL_PAD)
                l_features.append(get_h(rrc[0]) if len(rrc) > 0 else parser.DEPREL_PAD)
            else:
                # fill with padding
                features += [parser.PAD] * pad_f
                p_features += [parser.POS_PAD] * pad_pf
                l_features += [parser.DEPREL_PAD] * pad_lf

        return (features, p_features, l_features)

    def get_oracle(self):
        """
        Oracle determined transition on current state.
        Transitions are encoded as:
        0: Shift
        2 * deprel: LEFT-ARC
        2 * deprel + 1: RIGHT-ARC
        """
        if len(self.stack) < 2:
            return 0 # Shift

        s0 = self.stack[-1]
        s1 = self.stack[-2]
        h0 = s0.head
        h1 = s1.head
        l0 = s0.deprel
        l1 = s1.deprel

        if s1.id > 0 and h1 == s0.id and \
           not [x for x in self.buffer if x.head == s1.id]:
            # LEFT-ARC
            return l1 * 2
        elif s1.id >= 0 and h0 == s1.id and \
             not [x for x in self.buffer if x.head == s0.id]:
            # RIGHT-ARC
            return l0 * 2 + 1
        else:
            return None if len(self.buffer) == 0 else 0 # Shift

