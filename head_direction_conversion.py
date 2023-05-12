import re
import os 
from conllu import parse_incr


        
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
        


def build_folder(language):
    language_folder = []
    for file in os.listdir("C:/Users/steve/Documents/Stony Brook/mlwork/Universal Dependencies 2.11/ud-treebanks-v2.11"):
        if file[3:len(language) + 3] == language:
            path = "C:/Users/steve/Documents/Stony Brook/mlwork/Universal Dependencies 2.11/ud-treebanks-v2.11/" + file
            language_folder.append(path)
    return language_folder


def average_dl (folder, language, not_converted):
    if not_converted:
        total_dependencies = 0
        total_length = 0
        for dt_folder in folder:
            for file in os.listdir(dt_folder):
                if file[-6:] == "conllu":
                    file = dt_folder + "/" + file
                    with open(file, 'r', encoding="utf8") as f:
                        for sentence in parse_incr(f):
                            if len(sentence) <= 25:  # Exclude sentences longer than 25 words
                                for token in sentence:
                                    if token['head'] is not None:
                                        total_length += abs(token['head'] - token['id'])
                                        total_dependencies += 1
                    f.close()
        avg_length = total_length / total_dependencies
        print(language + " average dependency length:", avg_length)
    else:
        total_dependencies = 0
        total_length = 0
        for file in os.listdir(folder):
            file = folder + "/" + file
            with open(file, 'r', encoding="utf8") as f:
                # total length and dependencies were here
                for sentence in parse_incr(f):
                    if len(sentence) <= 25:  # Exclude sentences longer than 25 words
                        for token in sentence:
                            if token['head'] is not None:
                                total_length += abs(token['head'] - token['id'])
                                total_dependencies += 1
            f.close()
        avg_length = total_length / total_dependencies                
        print(language + " average dependency length:", avg_length)    

def convert_folder(language, folder):
    file_count = 1
    # print(jp_files)
    for dt_folder in folder:
        for file in os.listdir(dt_folder):
            if file[-6:] == "conllu":
                split_path = re.split("/", dt_folder)
                # print(split_path)
                file = "C:/Users/steve/Documents/Stony Brook/mlwork/Universal Dependencies 2.11/ud-treebanks-v2.11/" + split_path[-1] + "/" + file
                converted_conllu = change_dependency_direction(file)
                with open("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/" + language + "/test_" + str(file_count) + ".conllu", "w", encoding="utf-8") as file:
                    file.write(converted_conllu)
                file.close()
                file_count += 1

# english_files = build_folder("English")
# print()
# average_dl(english_files, "English", True)
# print()
# print("-------HEAD FINAL-------")

# jp_files = build_folder("Japanese")
# average_dl(jp_files, "Japanese", True)
# convert_folder("Japanese", jp_files)
# converted_jp_avg = average_dl("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/Japanese", "Japanese2", False)



# test_1 = reverse_words_around_root("C:/Users/steve/Documents/Stony Brook/mlwork/Universal Dependencies 2.11/ud-treebanks-v2.11/UD_German-GSD/de_gsd-ud-dev.conllu")
# with open("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/German/test_1.conllu", "w", encoding="utf-8") as file:
#     file.write(test_1)
# german_files = build_folder("German")
# average_dl(german_files, "German", True)
# convert_folder("German", german_files)
# converted_german_avg = average_dl("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/German", "German2", False)


# korean_files = build_folder("Korean")
# average_dl(korean_files, "Korean", True)
# convert_folder("Korean", korean_files)
# converted_korean_avg = average_dl("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/Korean", "Korean2", False)

# turkish_files = build_folder("Turkish")
# average_dl(turkish_files, "Turkish")
# convert_folder("Turkish", turkish_files)
# converted_turkish_avg = average_dl("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/Turkish", "Turkish2", False)

# print()
# print("-------HEAD INITIAL-------")
# italian_files = build_folder("Italian")
# average_dl(italian_files, "Italian")
# convert_folder("Italian", italian_files)
# converted_italian_avg = average_dl("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/Italian", "Italian2", False)

# irish_files = build_folder("Irish")
# average_dl(irish_files, "Irish")
# convert_folder("Irish", irish_files)
# converted_irish_avg = average_dl("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/Irish", "Irish2", False)

# indonesian_files = build_folder("Indonesian")
# average_dl(indonesian_files, "Indonesian")
# convert_folder("Indonesian", indonesian_files)
# converted_indonesian_avg = average_dl("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/Indonesian", "Indonesian2", False)

def individual_dl(file):
    with open(file, 'r', encoding="utf8") as f:
        total_dependencies = 0
        total_length = 0
        for sentence in parse_incr(f):
            if len(sentence) <= 25:  # Exclude sentences longer than 25 words
                for token in sentence:
                    if token['head'] is not None:
                        if token['head'] == 0:
                            pass
                        else:
                            total_length += abs(token['head'] - token['id'])
                            total_dependencies += 1

        average_dependency_length = total_length / total_dependencies        
    return average_dependency_length



x = change_dependency_direction("C:/Users/steve/Documents/Stony Brook/mlwork/Universal Dependencies 2.11/ud-treebanks-v2.11/UD_Korean-GSD/testconllu.conllu")
with open("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/Korean/test_20.conllu", "w", encoding="utf-8") as f:
    f.write(x)

z = individual_dl("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/Korean/converted_korean.conllu")
print("modified korean: " + str(z))

y = individual_dl("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/Korean/korean.conllu")
print("og Korean: " + str(y))

# flipped = reverse_words_around_root("C:/Users/steve/Documents/Stony Brook/mlwork/Universal Dependencies 2.11/ud-treebanks-v2.11/UD_Japanese-BCCWJ/ja_bccwj-ud-test.conllu")
# with open("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/Japanese/test_19.conllu", "w", encoding="utf-8") as file:
#     file.write(flipped)

# x = individual_dl("C:/Users/steve/Documents/Stony Brook/mlwork/Universal Dependencies 2.11/ud-treebanks-v2.11/UD_Japanese-BCCWJ/ja_bccwj-ud-test.conllu")

# print("Average DL OG: " + str(x))

# y = individual_dl("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/Japanese")
# print("Converted DL: " + str(y))
# with open("C:/Users/steve/Documents/Stony Brook/mlwork/Universal Dependencies 2.11/ud-treebanks-v2.11/UD_German-GSD/de_gsd-ud-dev.conllu", "r", encoding="utf-8") as file:
#     conllu_data = file.read()

# converted_conllu = convert_head_final_to_head_initial(conllu_data)

# with open("C:/Users/steve/Documents/Stony Brook/mlwork/converted UD trees/test.conllu", "w", encoding="utf-8") as file:
#     file.write(converted_conllu)