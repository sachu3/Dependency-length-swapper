from conllu import parse_incr

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