from abc import ABC, abstractmethod

class Feature:

    def __init__(self, type: str, range: str, meta_info: dict[str, str]) -> None:
        self.type = type
        self.range = range
        self.meta_info = meta_info

class Sequence:
    
    def __init__(self, sequence_info: str|dict, sequence_string: str, sequence_features: list[Feature] = None) -> None:
        self.info = sequence_info
        self.string = sequence_string
        self.features = sequence_features


class File:

    def __init__(self, name: str) -> None:
        self.name = name


class Parser(ABC):
    
    @abstractmethod
    def parse(self, file):
        pass
    
class GbParser(Parser):
    
    def parse(self, gb_file: File) -> Sequence:
        features_flag = False
        origin_flag = False
        sequence_features = []
        with open(gb_file.name, 'r') as f:
            for line in f:
                sequence_line_list = line.split()
                if sequence_line_list[0] == '//':
                    break
                # collect sequence info
                elif sequence_line_list[0] == 'LOCUS':
                    sequence_info = {
                        "Name": sequence_line_list[1],
                        "Size": sequence_line_list[2],
                        "Type of sequence": sequence_line_list[4],
                        "Topology": sequence_line_list[5],
                        "GenBank Division": sequence_line_list[6]
                    }
                # collect origin
                elif sequence_line_list[0] == 'ORIGIN':
                    origin_flag = True
                    sequence_string = ''
                    try:
                            sequence_features.append(Feature(
                                type_of_feature, 
                                range_of_feature, 
                                meta_dict_of_feature
                                ))
                    except: pass
                elif origin_flag:
                    if features_flag: 
                        features_flag = False
                    sequence_string += ''.join(el for el in sequence_line_list[1:])
                # collect sequence features
                elif sequence_line_list[0] == 'FEATURES':
                    features_flag = True
                # collect meta of feature
                elif features_flag:
                    if sequence_line_list[0][0] == '/':
                        meta_line = ' '.join(el for el in sequence_line_list)
                        meta_line_key, meta_line_value = meta_line.split('=')
                        meta_dict_of_feature[meta_line_key[1:]] = meta_line_value.replace('\"', '')
                # add feature to list of sequence features
                    else:
                        if len(sequence_line_list) == 2:
                            try:
                                sequence_features.append(Feature(
                                    type_of_feature, 
                                    range_of_feature, 
                                    meta_dict_of_feature))
                            except: pass
                            type_of_feature = sequence_line_list[0]
                            range_of_feature = sequence_line_list[1]
                            meta_dict_of_feature = {}
                        else:
                            meta_dict_of_feature[meta_line_key[1:]] += sequence_line_list[0]
        return Sequence(sequence_info, sequence_string, sequence_features)
                

        
class FastaParser(Parser):

    def parse(self, fasta_file: File)  -> list[Sequence]:
        sequence_list = []
        with open(fasta_file.name, 'r') as f:
            sequence_string = ''
            for line in f:
                if line[0] == '>':
                    if sequence_string:
                        sequence_list.append(Sequence(sequence_info, sequence_string))
                    sequence_info = line[1:]
                    sequence_string = ''
                else:
                    sequence_string = sequence_string + line
            if sequence_info: sequence_list.append(Sequence(sequence_info, sequence_string))
        return sequence_list
        
class FormatParserKeeper:
    """Keeps parsers for all available formats"""
    
    def __init__(self) -> None:
        self.available_formats_dict = dict()

        
    def add_format(self, format: str, parser: Parser) -> None:
        if format not in self.available_formats_dict:
            self.available_formats_dict[format] = parser


class ParserCaller:

    @staticmethod
    def call_parser(file: File, format_keeper: FormatParserKeeper) -> list[Sequence] | Sequence:
        format = file.name.partition('.')[-1]
        if format in format_keeper.available_formats_dict:
            seq = format_keeper.available_formats_dict[format].parse(file)
        else: 
            raise ValueError('Format is not supported')
        return seq