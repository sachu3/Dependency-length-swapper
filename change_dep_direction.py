def change_dependency_direction(conllu_file):
    with open(conllu_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    

    
    changes = {} # change of pair to new numbers
    modified_lines = []
    shift_map = {}  # To keep track of word index shifts
    new_pair_map = {}
    not_changed_yet_lines = []
    sent_length = 0
    for line in lines:
        if line.startswith('#') or line == "" or line == "\n":
            if sent_length > 0:
                continue
            sent_length = 0
            pass
        else:
            sent_length += 1
    for line in lines:
        if line.startswith('#') or line == "" or line == "\n":
            modified_lines.append(line) 
        else:
            fields = line.split('\t')
            original_index = int(fields[0])
            original_head_index = int(fields[6])
            shift_map[original_index] = original_head_index

            if original_head_index == 0:  # Root word, flip its position in the sentence
                new_head_index = sent_length - original_index + 1
                new_pair_map[new_head_index] = 0
                new_root_index = new_head_index
                old_root_index = original_index
                changes[(original_index, 0)] = [new_root_index, 0]
            elif not (line.startswith('#') or line == "" or line == "\n"): # add line to lines to go back to
                not_changed_yet_lines.append(line)
    runs = 0
    while len(not_changed_yet_lines) != 0 and runs < 30:
        # print(len(not_changed_yet_lines))
        for line in not_changed_yet_lines: # go back and change the rest of the lines after changing the position of the head
            fields = line.split('\t')
            original_index = int(fields[0])
            original_head_index = int(fields[6])
            shift_map[original_index] = original_head_index

            if shift_map[original_index] == old_root_index: # this word was original a dependent of the original root
                dependency_length = original_index - old_root_index
                if dependency_length > 0: # dependency length is positive, word was after root now it goes before the root
                    new_word_index = new_root_index - abs(dependency_length)
                    new_pair_map[new_word_index] = new_root_index
                    new_head_index = new_root_index
                    not_changed_yet_lines.remove(line)
                    changes[(original_index, original_head_index)] = [new_word_index, new_head_index]
                else: # dependency length is negative, word was before root now it goes after the root
                    new_word_index = new_root_index + abs(dependency_length)
                    new_pair_map[new_word_index] = new_root_index
                    new_head_index = new_root_index
                    not_changed_yet_lines.remove(line)
                    changes[(original_index, original_head_index)] = [new_word_index, new_head_index]
            else: # handle the dependents of the dependents
                new_changes = {}
                for original_pair in list(changes.keys()):
                    if original_head_index == original_pair[0]:
                        new_head_index = changes[original_pair][0]
                        dependency_length = original_index - original_head_index
                        new_changes[(original_index, original_head_index)] = [new_word_index, new_head_index]
                        if dependency_length > 0: # dependency length is positive, word was after its dependent, not it goes before the dependent
                            new_word_index = new_head_index - abs(dependency_length)
                            new_pair_map[new_word_index] = new_head_index
                            new_changes[(original_index, original_head_index)] = [new_word_index, new_head_index]
                            not_changed_yet_lines.remove(line)
                        else: # dependency length is negative, word was before its dependent, now it goes after its dependent
                            new_word_index = new_head_index + abs(dependency_length)
                            new_pair_map[new_word_index] = new_head_index
                            not_changed_yet_lines.remove(line)
                            new_changes[(original_index, original_head_index)] = [new_word_index, new_head_index]
                    changes = {**changes, **new_changes}
        runs += 1



    
   
    keys = list(new_pair_map.keys())
    keys.sort()
    sorted_positions = {i: new_pair_map[i] for i in keys}
    i = 0
    sorted_positions_keys = list(sorted_positions.keys())
    for line in lines:
        if line.startswith('#') or line == "\n" or line == "":
            continue
        fields = line.split("\t")
        # fields[0] = str(sorted_positions_keys[i])
        fields[6] = str(sorted_positions[sorted_positions_keys[i]])
        modified_lines.append('\t'.join(fields))
        i += 1


    
    modified_conllu = ''.join(modified_lines)

    return modified_conllu