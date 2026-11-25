# Generated from spec/v1.0/grammar/PhiSQL.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,96,490,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,2,33,
        7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,2,39,7,39,
        2,40,7,40,2,41,7,41,1,0,1,0,1,0,5,0,88,8,0,10,0,12,0,91,9,0,1,0,
        1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,106,8,1,1,2,
        1,2,1,2,1,2,3,2,112,8,2,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,3,3,142,8,3,1,3,1,3,1,3,1,3,3,3,148,8,3,1,4,1,4,1,4,5,4,
        153,8,4,10,4,12,4,156,9,4,1,5,1,5,1,5,1,5,1,6,1,6,1,7,1,7,1,7,3,
        7,167,8,7,1,8,1,8,1,8,1,8,1,9,1,9,1,9,1,9,5,9,177,8,9,10,9,12,9,
        180,9,9,3,9,182,8,9,1,9,1,9,1,10,1,10,1,10,1,10,1,10,1,11,1,11,1,
        11,1,11,3,11,195,8,11,1,11,1,11,3,11,199,8,11,1,11,3,11,202,8,11,
        1,12,1,12,1,12,1,12,5,12,208,8,12,10,12,12,12,211,9,12,1,13,1,13,
        1,13,1,13,3,13,217,8,13,1,14,1,14,1,14,1,14,1,14,3,14,224,8,14,1,
        14,1,14,3,14,228,8,14,1,14,3,14,231,8,14,1,15,1,15,1,15,1,15,1,15,
        1,15,1,15,3,15,240,8,15,1,15,1,15,3,15,244,8,15,1,15,1,15,1,15,1,
        15,3,15,250,8,15,1,15,3,15,253,8,15,1,16,1,16,1,16,1,16,1,16,1,16,
        1,16,1,16,3,16,263,8,16,3,16,265,8,16,1,16,3,16,268,8,16,1,16,1,
        16,1,16,3,16,273,8,16,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,
        17,3,17,284,8,17,1,18,1,18,1,18,1,18,1,18,1,18,1,18,1,19,1,19,1,
        19,1,19,3,19,297,8,19,1,19,1,19,3,19,301,8,19,1,19,1,19,3,19,305,
        8,19,1,19,1,19,1,19,1,19,3,19,311,8,19,1,19,3,19,314,8,19,1,20,1,
        20,1,20,1,20,3,20,320,8,20,1,20,1,20,1,20,1,20,3,20,326,8,20,1,20,
        1,20,1,20,3,20,331,8,20,1,20,1,20,1,20,1,20,1,20,3,20,338,8,20,1,
        20,3,20,341,8,20,1,20,3,20,344,8,20,3,20,346,8,20,1,21,1,21,1,21,
        1,22,1,22,1,22,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,
        1,23,1,23,1,23,3,23,367,8,23,1,23,1,23,1,23,5,23,372,8,23,10,23,
        12,23,375,9,23,1,24,1,24,1,24,5,24,380,8,24,10,24,12,24,383,9,24,
        1,25,1,25,1,25,3,25,388,8,25,1,26,1,26,1,26,1,26,1,26,1,27,1,27,
        3,27,397,8,27,1,28,1,28,1,29,1,29,3,29,403,8,29,1,29,1,29,1,30,1,
        30,1,30,1,30,1,30,5,30,412,8,30,10,30,12,30,415,9,30,1,31,1,31,1,
        31,1,32,1,32,1,32,5,32,423,8,32,10,32,12,32,426,9,32,1,33,1,33,1,
        33,1,33,1,33,3,33,433,8,33,1,34,1,34,1,34,1,34,1,34,3,34,440,8,34,
        1,35,1,35,1,36,1,36,1,36,5,36,447,8,36,10,36,12,36,450,9,36,1,37,
        1,37,1,37,1,37,1,38,1,38,1,38,1,38,1,38,1,38,1,38,1,38,1,38,3,38,
        465,8,38,1,38,1,38,1,38,5,38,470,8,38,10,38,12,38,473,9,38,1,39,
        1,39,1,40,1,40,1,40,1,40,5,40,481,8,40,10,40,12,40,484,9,40,1,40,
        1,40,1,41,1,41,1,41,0,2,46,76,42,0,2,4,6,8,10,12,14,16,18,20,22,
        24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,66,
        68,70,72,74,76,78,80,82,0,11,1,0,23,26,1,0,91,92,1,0,45,46,2,0,90,
        90,92,93,1,0,38,39,1,0,71,75,2,0,40,40,91,91,2,0,29,29,77,89,2,0,
        54,55,91,91,2,0,5,5,10,13,1,0,90,93,516,0,89,1,0,0,0,2,105,1,0,0,
        0,4,107,1,0,0,0,6,113,1,0,0,0,8,149,1,0,0,0,10,157,1,0,0,0,12,161,
        1,0,0,0,14,166,1,0,0,0,16,168,1,0,0,0,18,172,1,0,0,0,20,185,1,0,
        0,0,22,190,1,0,0,0,24,203,1,0,0,0,26,212,1,0,0,0,28,218,1,0,0,0,
        30,232,1,0,0,0,32,254,1,0,0,0,34,274,1,0,0,0,36,285,1,0,0,0,38,292,
        1,0,0,0,40,345,1,0,0,0,42,347,1,0,0,0,44,350,1,0,0,0,46,366,1,0,
        0,0,48,376,1,0,0,0,50,387,1,0,0,0,52,389,1,0,0,0,54,396,1,0,0,0,
        56,398,1,0,0,0,58,402,1,0,0,0,60,406,1,0,0,0,62,416,1,0,0,0,64,419,
        1,0,0,0,66,432,1,0,0,0,68,434,1,0,0,0,70,441,1,0,0,0,72,443,1,0,
        0,0,74,451,1,0,0,0,76,464,1,0,0,0,78,474,1,0,0,0,80,476,1,0,0,0,
        82,487,1,0,0,0,84,85,3,2,1,0,85,86,5,1,0,0,86,88,1,0,0,0,87,84,1,
        0,0,0,88,91,1,0,0,0,89,87,1,0,0,0,89,90,1,0,0,0,90,92,1,0,0,0,91,
        89,1,0,0,0,92,93,5,0,0,1,93,1,1,0,0,0,94,106,3,4,2,0,95,106,3,6,
        3,0,96,106,3,22,11,0,97,106,3,24,12,0,98,106,3,28,14,0,99,106,3,
        30,15,0,100,106,3,32,16,0,101,106,3,34,17,0,102,106,3,36,18,0,103,
        106,3,38,19,0,104,106,3,40,20,0,105,94,1,0,0,0,105,95,1,0,0,0,105,
        96,1,0,0,0,105,97,1,0,0,0,105,98,1,0,0,0,105,99,1,0,0,0,105,100,
        1,0,0,0,105,101,1,0,0,0,105,102,1,0,0,0,105,103,1,0,0,0,105,104,
        1,0,0,0,106,3,1,0,0,0,107,108,5,14,0,0,108,111,5,91,0,0,109,110,
        5,15,0,0,110,112,5,92,0,0,111,109,1,0,0,0,111,112,1,0,0,0,112,5,
        1,0,0,0,113,147,5,16,0,0,114,115,5,17,0,0,115,116,5,19,0,0,116,117,
        5,21,0,0,117,118,5,22,0,0,118,148,5,92,0,0,119,120,5,18,0,0,120,
        121,5,19,0,0,121,122,5,21,0,0,122,123,5,22,0,0,123,124,5,92,0,0,
        124,125,5,20,0,0,125,126,5,21,0,0,126,127,5,22,0,0,127,148,5,92,
        0,0,128,129,7,0,0,0,129,130,5,2,0,0,130,131,3,8,4,0,131,132,5,3,
        0,0,132,148,1,0,0,0,133,134,5,27,0,0,134,135,5,28,0,0,135,136,5,
        2,0,0,136,137,3,8,4,0,137,138,5,3,0,0,138,148,1,0,0,0,139,141,5,
        91,0,0,140,142,5,91,0,0,141,140,1,0,0,0,141,142,1,0,0,0,142,143,
        1,0,0,0,143,144,5,2,0,0,144,145,3,8,4,0,145,146,5,3,0,0,146,148,
        1,0,0,0,147,114,1,0,0,0,147,119,1,0,0,0,147,128,1,0,0,0,147,133,
        1,0,0,0,147,139,1,0,0,0,148,7,1,0,0,0,149,154,3,10,5,0,150,151,5,
        4,0,0,151,153,3,10,5,0,152,150,1,0,0,0,153,156,1,0,0,0,154,152,1,
        0,0,0,154,155,1,0,0,0,155,9,1,0,0,0,156,154,1,0,0,0,157,158,3,12,
        6,0,158,159,5,5,0,0,159,160,3,14,7,0,160,11,1,0,0,0,161,162,7,1,
        0,0,162,13,1,0,0,0,163,167,3,82,41,0,164,167,3,16,8,0,165,167,3,
        18,9,0,166,163,1,0,0,0,166,164,1,0,0,0,166,165,1,0,0,0,167,15,1,
        0,0,0,168,169,5,2,0,0,169,170,3,8,4,0,170,171,5,3,0,0,171,17,1,0,
        0,0,172,181,5,6,0,0,173,178,3,14,7,0,174,175,5,4,0,0,175,177,3,14,
        7,0,176,174,1,0,0,0,177,180,1,0,0,0,178,176,1,0,0,0,178,179,1,0,
        0,0,179,182,1,0,0,0,180,178,1,0,0,0,181,173,1,0,0,0,181,182,1,0,
        0,0,182,183,1,0,0,0,183,184,5,7,0,0,184,19,1,0,0,0,185,186,5,56,
        0,0,186,187,5,2,0,0,187,188,3,8,4,0,188,189,5,3,0,0,189,21,1,0,0,
        0,190,191,5,29,0,0,191,194,3,64,32,0,192,193,5,35,0,0,193,195,3,
        68,34,0,194,192,1,0,0,0,194,195,1,0,0,0,195,198,1,0,0,0,196,197,
        5,36,0,0,197,199,3,76,38,0,198,196,1,0,0,0,198,199,1,0,0,0,199,201,
        1,0,0,0,200,202,3,20,10,0,201,200,1,0,0,0,201,202,1,0,0,0,202,23,
        1,0,0,0,203,204,5,30,0,0,204,209,3,26,13,0,205,206,5,4,0,0,206,208,
        3,26,13,0,207,205,1,0,0,0,208,211,1,0,0,0,209,207,1,0,0,0,209,210,
        1,0,0,0,210,25,1,0,0,0,211,209,1,0,0,0,212,213,3,66,33,0,213,214,
        5,37,0,0,214,216,3,68,34,0,215,217,3,20,10,0,216,215,1,0,0,0,216,
        217,1,0,0,0,217,27,1,0,0,0,218,223,5,31,0,0,219,220,5,32,0,0,220,
        224,3,80,40,0,221,222,5,33,0,0,222,224,5,92,0,0,223,219,1,0,0,0,
        223,221,1,0,0,0,224,227,1,0,0,0,225,226,5,34,0,0,226,228,3,64,32,
        0,227,225,1,0,0,0,227,228,1,0,0,0,228,230,1,0,0,0,229,231,3,20,10,
        0,230,229,1,0,0,0,230,231,1,0,0,0,231,29,1,0,0,0,232,233,5,41,0,
        0,233,234,5,76,0,0,234,235,5,92,0,0,235,236,5,42,0,0,236,239,5,92,
        0,0,237,238,5,43,0,0,238,240,5,93,0,0,239,237,1,0,0,0,239,240,1,
        0,0,0,240,243,1,0,0,0,241,242,5,44,0,0,242,244,7,2,0,0,243,241,1,
        0,0,0,243,244,1,0,0,0,244,245,1,0,0,0,245,246,5,35,0,0,246,249,3,
        68,34,0,247,248,5,36,0,0,248,250,3,76,38,0,249,247,1,0,0,0,249,250,
        1,0,0,0,250,252,1,0,0,0,251,253,3,20,10,0,252,251,1,0,0,0,252,253,
        1,0,0,0,253,31,1,0,0,0,254,255,5,41,0,0,255,256,5,47,0,0,256,257,
        5,92,0,0,257,258,5,32,0,0,258,264,3,80,40,0,259,262,5,51,0,0,260,
        261,5,52,0,0,261,263,5,91,0,0,262,260,1,0,0,0,262,263,1,0,0,0,263,
        265,1,0,0,0,264,259,1,0,0,0,264,265,1,0,0,0,265,267,1,0,0,0,266,
        268,5,53,0,0,267,266,1,0,0,0,267,268,1,0,0,0,268,269,1,0,0,0,269,
        270,5,35,0,0,270,272,3,68,34,0,271,273,3,20,10,0,272,271,1,0,0,0,
        272,273,1,0,0,0,273,33,1,0,0,0,274,275,5,41,0,0,275,276,5,48,0,0,
        276,277,5,49,0,0,277,278,5,92,0,0,278,279,5,50,0,0,279,280,5,92,
        0,0,280,281,5,35,0,0,281,283,3,68,34,0,282,284,3,20,10,0,283,282,
        1,0,0,0,283,284,1,0,0,0,284,35,1,0,0,0,285,286,5,41,0,0,286,287,
        5,54,0,0,287,288,5,92,0,0,288,289,5,55,0,0,289,290,5,92,0,0,290,
        291,3,20,10,0,291,37,1,0,0,0,292,293,5,57,0,0,293,296,5,58,0,0,294,
        295,5,59,0,0,295,297,3,80,40,0,296,294,1,0,0,0,296,297,1,0,0,0,297,
        300,1,0,0,0,298,299,5,60,0,0,299,301,5,92,0,0,300,298,1,0,0,0,300,
        301,1,0,0,0,301,304,1,0,0,0,302,303,5,61,0,0,303,305,5,92,0,0,304,
        302,1,0,0,0,304,305,1,0,0,0,305,306,1,0,0,0,306,307,5,35,0,0,307,
        310,3,68,34,0,308,309,5,36,0,0,309,311,3,76,38,0,310,308,1,0,0,0,
        310,311,1,0,0,0,311,313,1,0,0,0,312,314,3,20,10,0,313,312,1,0,0,
        0,313,314,1,0,0,0,314,39,1,0,0,0,315,316,5,62,0,0,316,317,5,63,0,
        0,317,319,3,42,21,0,318,320,3,44,22,0,319,318,1,0,0,0,319,320,1,
        0,0,0,320,346,1,0,0,0,321,322,5,64,0,0,322,323,5,65,0,0,323,325,
        3,42,21,0,324,326,3,44,22,0,325,324,1,0,0,0,325,326,1,0,0,0,326,
        346,1,0,0,0,327,328,5,66,0,0,328,330,3,42,21,0,329,331,3,44,22,0,
        330,329,1,0,0,0,330,331,1,0,0,0,331,346,1,0,0,0,332,333,5,68,0,0,
        333,334,3,48,24,0,334,335,5,21,0,0,335,337,3,58,29,0,336,338,3,44,
        22,0,337,336,1,0,0,0,337,338,1,0,0,0,338,340,1,0,0,0,339,341,3,60,
        30,0,340,339,1,0,0,0,340,341,1,0,0,0,341,343,1,0,0,0,342,344,3,62,
        31,0,343,342,1,0,0,0,343,344,1,0,0,0,344,346,1,0,0,0,345,315,1,0,
        0,0,345,321,1,0,0,0,345,327,1,0,0,0,345,332,1,0,0,0,346,41,1,0,0,
        0,347,348,5,67,0,0,348,349,5,92,0,0,349,43,1,0,0,0,350,351,5,36,
        0,0,351,352,3,46,23,0,352,45,1,0,0,0,353,354,6,23,-1,0,354,355,3,
        56,28,0,355,356,5,67,0,0,356,357,3,80,40,0,357,367,1,0,0,0,358,359,
        3,56,28,0,359,360,3,78,39,0,360,361,7,3,0,0,361,367,1,0,0,0,362,
        363,5,2,0,0,363,364,3,46,23,0,364,365,5,3,0,0,365,367,1,0,0,0,366,
        353,1,0,0,0,366,358,1,0,0,0,366,362,1,0,0,0,367,373,1,0,0,0,368,
        369,10,1,0,0,369,370,7,4,0,0,370,372,3,46,23,2,371,368,1,0,0,0,372,
        375,1,0,0,0,373,371,1,0,0,0,373,374,1,0,0,0,374,47,1,0,0,0,375,373,
        1,0,0,0,376,381,3,50,25,0,377,378,5,4,0,0,378,380,3,50,25,0,379,
        377,1,0,0,0,380,383,1,0,0,0,381,379,1,0,0,0,381,382,1,0,0,0,382,
        49,1,0,0,0,383,381,1,0,0,0,384,388,5,8,0,0,385,388,3,52,26,0,386,
        388,3,56,28,0,387,384,1,0,0,0,387,385,1,0,0,0,387,386,1,0,0,0,388,
        51,1,0,0,0,389,390,7,5,0,0,390,391,5,2,0,0,391,392,3,54,27,0,392,
        393,5,3,0,0,393,53,1,0,0,0,394,397,5,8,0,0,395,397,3,56,28,0,396,
        394,1,0,0,0,396,395,1,0,0,0,397,55,1,0,0,0,398,399,7,6,0,0,399,57,
        1,0,0,0,400,401,5,91,0,0,401,403,5,9,0,0,402,400,1,0,0,0,402,403,
        1,0,0,0,403,404,1,0,0,0,404,405,5,91,0,0,405,59,1,0,0,0,406,407,
        5,43,0,0,407,408,5,69,0,0,408,413,3,56,28,0,409,410,5,4,0,0,410,
        412,3,56,28,0,411,409,1,0,0,0,412,415,1,0,0,0,413,411,1,0,0,0,413,
        414,1,0,0,0,414,61,1,0,0,0,415,413,1,0,0,0,416,417,5,70,0,0,417,
        418,5,93,0,0,418,63,1,0,0,0,419,424,3,66,33,0,420,421,5,4,0,0,421,
        423,3,66,33,0,422,420,1,0,0,0,423,426,1,0,0,0,424,422,1,0,0,0,424,
        425,1,0,0,0,425,65,1,0,0,0,426,424,1,0,0,0,427,433,5,91,0,0,428,
        429,5,76,0,0,429,430,5,2,0,0,430,431,5,92,0,0,431,433,5,3,0,0,432,
        427,1,0,0,0,432,428,1,0,0,0,433,67,1,0,0,0,434,439,3,70,35,0,435,
        436,5,2,0,0,436,437,3,72,36,0,437,438,5,3,0,0,438,440,1,0,0,0,439,
        435,1,0,0,0,439,440,1,0,0,0,440,69,1,0,0,0,441,442,7,7,0,0,442,71,
        1,0,0,0,443,448,3,74,37,0,444,445,5,4,0,0,445,447,3,74,37,0,446,
        444,1,0,0,0,447,450,1,0,0,0,448,446,1,0,0,0,448,449,1,0,0,0,449,
        73,1,0,0,0,450,448,1,0,0,0,451,452,7,8,0,0,452,453,5,5,0,0,453,454,
        3,14,7,0,454,75,1,0,0,0,455,456,6,38,-1,0,456,457,5,40,0,0,457,458,
        3,78,39,0,458,459,5,93,0,0,459,465,1,0,0,0,460,461,5,2,0,0,461,462,
        3,76,38,0,462,463,5,3,0,0,463,465,1,0,0,0,464,455,1,0,0,0,464,460,
        1,0,0,0,465,471,1,0,0,0,466,467,10,1,0,0,467,468,7,4,0,0,468,470,
        3,76,38,2,469,466,1,0,0,0,470,473,1,0,0,0,471,469,1,0,0,0,471,472,
        1,0,0,0,472,77,1,0,0,0,473,471,1,0,0,0,474,475,7,9,0,0,475,79,1,
        0,0,0,476,477,5,2,0,0,477,482,5,92,0,0,478,479,5,4,0,0,479,481,5,
        92,0,0,480,478,1,0,0,0,481,484,1,0,0,0,482,480,1,0,0,0,482,483,1,
        0,0,0,483,485,1,0,0,0,484,482,1,0,0,0,485,486,5,3,0,0,486,81,1,0,
        0,0,487,488,7,10,0,0,488,83,1,0,0,0,52,89,105,111,141,147,154,166,
        178,181,194,198,201,209,216,223,227,230,239,243,249,252,262,264,
        267,272,283,296,300,304,310,313,319,325,330,337,340,343,345,366,
        373,381,387,396,402,413,424,432,439,448,464,471,482
    ]

class PhiSQLParser ( Parser ):

    grammarFileName = "PhiSQL.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "';'", "'('", "')'", "','", "'='", "'['", 
                     "']'", "'*'", "'.'", "'>'", "'>='", "'<'", "'<='", 
                     "'POLICY'", "'DESCRIPTION'", "'CONFIGURE'", "'CRYPTO'", 
                     "'FPE'", "'KEY'", "'TWEAK'", "'FROM'", "'ENV'", "'SPLITTING'", 
                     "'PDF'", "'POSTFILTERS'", "'ANALYSIS'", "'GRAPHICAL'", 
                     "'BOX'", "'REDACT'", "'DEIDENTIFY'", "'IGNORE'", "'TERMS'", 
                     "'PATTERN'", "'FOR'", "'WITH'", "'WHERE'", "'AS'", 
                     "'AND'", "'OR'", "'CONFIDENCE'", "'DEFINE'", "'MATCHING'", 
                     "'GROUP'", "'CASE'", "'SENSITIVE'", "'INSENSITIVE'", 
                     "'DICTIONARY'", "'SECTION'", "'START'", "'END'", "'FUZZY'", 
                     "'SENSITIVITY'", "'CAPITALIZED'", "'GENERATOR'", "'TYPE'", 
                     "'OPTIONS'", "'DETECT'", "'PHEYE'", "'LABELS'", "'ENDPOINT'", 
                     "'MODEL'", "'FIND'", "'PII'", "'DISCOVER'", "'ENTITIES'", 
                     "'SCAN'", "'IN'", "'SELECT'", "'BY'", "'LIMIT'", "'COUNT'", 
                     "'AVG'", "'SUM'", "'MIN'", "'MAX'", "'IDENTIFIER'", 
                     "'MASK'", "'ENCRYPT'", "'FPE_ENCRYPT'", "'HASH_SHA256'", 
                     "'RANDOM_REPLACE'", "'STATIC_REPLACE'", "'LAST_4'", 
                     "'TRUNCATE_TO_YEAR'", "'TRUNCATE'", "'SHIFT'", "'RELATIVE'", 
                     "'ABBREVIATE'", "'MAP_REPLACE'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "POLICY", "DESCRIPTION", 
                      "CONFIGURE", "CRYPTO", "FPE", "KEY", "TWEAK", "FROM", 
                      "ENV", "SPLITTING", "PDF", "POSTFILTERS", "ANALYSIS", 
                      "GRAPHICAL", "BOX", "REDACT", "DEIDENTIFY", "IGNORE", 
                      "TERMS", "PATTERN", "FOR", "WITH", "WHERE", "AS", 
                      "AND", "OR", "CONFIDENCE", "DEFINE", "MATCHING", "GROUP", 
                      "CASE", "SENSITIVE", "INSENSITIVE", "DICTIONARY", 
                      "SECTION", "START", "END", "FUZZY", "SENSITIVITY", 
                      "CAPITALIZED", "GENERATOR", "TYPE", "OPTIONS", "DETECT", 
                      "PHEYE", "LABELS", "ENDPOINT", "MODEL", "FIND", "PII", 
                      "DISCOVER", "ENTITIES", "SCAN", "IN", "SELECT", "BY", 
                      "LIMIT", "COUNT", "AVG", "SUM", "MIN", "MAX", "IDENTIFIER_KW", 
                      "MASK", "ENCRYPT", "FPE_ENCRYPT", "HASH_SHA256", "RANDOM_REPLACE", 
                      "STATIC_REPLACE", "LAST_4", "TRUNCATE_TO_YEAR", "TRUNCATE", 
                      "SHIFT", "RELATIVE", "ABBREVIATE", "MAP_REPLACE", 
                      "BOOLEAN_LITERAL", "ID", "STRING_LITERAL", "NUMERIC_LITERAL", 
                      "LINE_COMMENT", "BLOCK_COMMENT", "WS" ]

    RULE_document = 0
    RULE_statement = 1
    RULE_policyDecl = 2
    RULE_configureStmt = 3
    RULE_settingList = 4
    RULE_setting = 5
    RULE_settingKey = 6
    RULE_settingValue = 7
    RULE_objectValue = 8
    RULE_arrayValue = 9
    RULE_optionsClause = 10
    RULE_redactStmt = 11
    RULE_deidentifyStmt = 12
    RULE_entityAssignment = 13
    RULE_ignoreStmt = 14
    RULE_defineIdentifierStmt = 15
    RULE_defineDictionaryStmt = 16
    RULE_defineSectionStmt = 17
    RULE_defineGeneratorStmt = 18
    RULE_detectStmt = 19
    RULE_discoveryStmt = 20
    RULE_inClause = 21
    RULE_whereDiscovery = 22
    RULE_discoveryPredicate = 23
    RULE_projectionList = 24
    RULE_projection = 25
    RULE_aggregate = 26
    RULE_aggArg = 27
    RULE_columnRef = 28
    RULE_findingsRef = 29
    RULE_groupByClause = 30
    RULE_limitClause = 31
    RULE_entityList = 32
    RULE_entityType = 33
    RULE_strategyExpr = 34
    RULE_strategyName = 35
    RULE_strategyArgs = 36
    RULE_namedArg = 37
    RULE_predicate = 38
    RULE_compareOp = 39
    RULE_stringList = 40
    RULE_literal = 41

    ruleNames =  [ "document", "statement", "policyDecl", "configureStmt", 
                   "settingList", "setting", "settingKey", "settingValue", 
                   "objectValue", "arrayValue", "optionsClause", "redactStmt", 
                   "deidentifyStmt", "entityAssignment", "ignoreStmt", "defineIdentifierStmt", 
                   "defineDictionaryStmt", "defineSectionStmt", "defineGeneratorStmt", 
                   "detectStmt", "discoveryStmt", "inClause", "whereDiscovery", 
                   "discoveryPredicate", "projectionList", "projection", 
                   "aggregate", "aggArg", "columnRef", "findingsRef", "groupByClause", 
                   "limitClause", "entityList", "entityType", "strategyExpr", 
                   "strategyName", "strategyArgs", "namedArg", "predicate", 
                   "compareOp", "stringList", "literal" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    POLICY=14
    DESCRIPTION=15
    CONFIGURE=16
    CRYPTO=17
    FPE=18
    KEY=19
    TWEAK=20
    FROM=21
    ENV=22
    SPLITTING=23
    PDF=24
    POSTFILTERS=25
    ANALYSIS=26
    GRAPHICAL=27
    BOX=28
    REDACT=29
    DEIDENTIFY=30
    IGNORE=31
    TERMS=32
    PATTERN=33
    FOR=34
    WITH=35
    WHERE=36
    AS=37
    AND=38
    OR=39
    CONFIDENCE=40
    DEFINE=41
    MATCHING=42
    GROUP=43
    CASE=44
    SENSITIVE=45
    INSENSITIVE=46
    DICTIONARY=47
    SECTION=48
    START=49
    END=50
    FUZZY=51
    SENSITIVITY=52
    CAPITALIZED=53
    GENERATOR=54
    TYPE=55
    OPTIONS=56
    DETECT=57
    PHEYE=58
    LABELS=59
    ENDPOINT=60
    MODEL=61
    FIND=62
    PII=63
    DISCOVER=64
    ENTITIES=65
    SCAN=66
    IN=67
    SELECT=68
    BY=69
    LIMIT=70
    COUNT=71
    AVG=72
    SUM=73
    MIN=74
    MAX=75
    IDENTIFIER_KW=76
    MASK=77
    ENCRYPT=78
    FPE_ENCRYPT=79
    HASH_SHA256=80
    RANDOM_REPLACE=81
    STATIC_REPLACE=82
    LAST_4=83
    TRUNCATE_TO_YEAR=84
    TRUNCATE=85
    SHIFT=86
    RELATIVE=87
    ABBREVIATE=88
    MAP_REPLACE=89
    BOOLEAN_LITERAL=90
    ID=91
    STRING_LITERAL=92
    NUMERIC_LITERAL=93
    LINE_COMMENT=94
    BLOCK_COMMENT=95
    WS=96

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class DocumentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(PhiSQLParser.EOF, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PhiSQLParser.StatementContext)
            else:
                return self.getTypedRuleContext(PhiSQLParser.StatementContext,i)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_document

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDocument" ):
                listener.enterDocument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDocument" ):
                listener.exitDocument(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDocument" ):
                return visitor.visitDocument(self)
            else:
                return visitor.visitChildren(self)




    def document(self):

        localctx = PhiSQLParser.DocumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_document)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((((_la - 14)) & ~0x3f) == 0 and ((1 << (_la - 14)) & 23934169247875077) != 0):
                self.state = 84
                self.statement()
                self.state = 85
                self.match(PhiSQLParser.T__0)
                self.state = 91
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 92
            self.match(PhiSQLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def policyDecl(self):
            return self.getTypedRuleContext(PhiSQLParser.PolicyDeclContext,0)


        def configureStmt(self):
            return self.getTypedRuleContext(PhiSQLParser.ConfigureStmtContext,0)


        def redactStmt(self):
            return self.getTypedRuleContext(PhiSQLParser.RedactStmtContext,0)


        def deidentifyStmt(self):
            return self.getTypedRuleContext(PhiSQLParser.DeidentifyStmtContext,0)


        def ignoreStmt(self):
            return self.getTypedRuleContext(PhiSQLParser.IgnoreStmtContext,0)


        def defineIdentifierStmt(self):
            return self.getTypedRuleContext(PhiSQLParser.DefineIdentifierStmtContext,0)


        def defineDictionaryStmt(self):
            return self.getTypedRuleContext(PhiSQLParser.DefineDictionaryStmtContext,0)


        def defineSectionStmt(self):
            return self.getTypedRuleContext(PhiSQLParser.DefineSectionStmtContext,0)


        def defineGeneratorStmt(self):
            return self.getTypedRuleContext(PhiSQLParser.DefineGeneratorStmtContext,0)


        def detectStmt(self):
            return self.getTypedRuleContext(PhiSQLParser.DetectStmtContext,0)


        def discoveryStmt(self):
            return self.getTypedRuleContext(PhiSQLParser.DiscoveryStmtContext,0)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = PhiSQLParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_statement)
        try:
            self.state = 105
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 94
                self.policyDecl()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 95
                self.configureStmt()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 96
                self.redactStmt()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 97
                self.deidentifyStmt()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 98
                self.ignoreStmt()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 99
                self.defineIdentifierStmt()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 100
                self.defineDictionaryStmt()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 101
                self.defineSectionStmt()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 102
                self.defineGeneratorStmt()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 103
                self.detectStmt()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 104
                self.discoveryStmt()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PolicyDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.policyName = None # Token
            self.description = None # Token

        def POLICY(self):
            return self.getToken(PhiSQLParser.POLICY, 0)

        def ID(self):
            return self.getToken(PhiSQLParser.ID, 0)

        def DESCRIPTION(self):
            return self.getToken(PhiSQLParser.DESCRIPTION, 0)

        def STRING_LITERAL(self):
            return self.getToken(PhiSQLParser.STRING_LITERAL, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_policyDecl

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPolicyDecl" ):
                listener.enterPolicyDecl(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPolicyDecl" ):
                listener.exitPolicyDecl(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPolicyDecl" ):
                return visitor.visitPolicyDecl(self)
            else:
                return visitor.visitChildren(self)




    def policyDecl(self):

        localctx = PhiSQLParser.PolicyDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_policyDecl)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 107
            self.match(PhiSQLParser.POLICY)
            self.state = 108
            localctx.policyName = self.match(PhiSQLParser.ID)
            self.state = 111
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==15:
                self.state = 109
                self.match(PhiSQLParser.DESCRIPTION)
                self.state = 110
                localctx.description = self.match(PhiSQLParser.STRING_LITERAL)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConfigureStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.cryptoKeyEnv = None # Token
            self.fpeKeyEnv = None # Token
            self.fpeTweakEnv = None # Token
            self.configBlock = None # Token
            self.blockName = None # Token
            self.subName = None # Token

        def CONFIGURE(self):
            return self.getToken(PhiSQLParser.CONFIGURE, 0)

        def CRYPTO(self):
            return self.getToken(PhiSQLParser.CRYPTO, 0)

        def KEY(self):
            return self.getToken(PhiSQLParser.KEY, 0)

        def FROM(self, i:int=None):
            if i is None:
                return self.getTokens(PhiSQLParser.FROM)
            else:
                return self.getToken(PhiSQLParser.FROM, i)

        def ENV(self, i:int=None):
            if i is None:
                return self.getTokens(PhiSQLParser.ENV)
            else:
                return self.getToken(PhiSQLParser.ENV, i)

        def FPE(self):
            return self.getToken(PhiSQLParser.FPE, 0)

        def TWEAK(self):
            return self.getToken(PhiSQLParser.TWEAK, 0)

        def settingList(self):
            return self.getTypedRuleContext(PhiSQLParser.SettingListContext,0)


        def GRAPHICAL(self):
            return self.getToken(PhiSQLParser.GRAPHICAL, 0)

        def BOX(self):
            return self.getToken(PhiSQLParser.BOX, 0)

        def STRING_LITERAL(self, i:int=None):
            if i is None:
                return self.getTokens(PhiSQLParser.STRING_LITERAL)
            else:
                return self.getToken(PhiSQLParser.STRING_LITERAL, i)

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(PhiSQLParser.ID)
            else:
                return self.getToken(PhiSQLParser.ID, i)

        def SPLITTING(self):
            return self.getToken(PhiSQLParser.SPLITTING, 0)

        def PDF(self):
            return self.getToken(PhiSQLParser.PDF, 0)

        def POSTFILTERS(self):
            return self.getToken(PhiSQLParser.POSTFILTERS, 0)

        def ANALYSIS(self):
            return self.getToken(PhiSQLParser.ANALYSIS, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_configureStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterConfigureStmt" ):
                listener.enterConfigureStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitConfigureStmt" ):
                listener.exitConfigureStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConfigureStmt" ):
                return visitor.visitConfigureStmt(self)
            else:
                return visitor.visitChildren(self)




    def configureStmt(self):

        localctx = PhiSQLParser.ConfigureStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_configureStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            self.match(PhiSQLParser.CONFIGURE)
            self.state = 147
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [17]:
                self.state = 114
                self.match(PhiSQLParser.CRYPTO)
                self.state = 115
                self.match(PhiSQLParser.KEY)
                self.state = 116
                self.match(PhiSQLParser.FROM)
                self.state = 117
                self.match(PhiSQLParser.ENV)
                self.state = 118
                localctx.cryptoKeyEnv = self.match(PhiSQLParser.STRING_LITERAL)
                pass
            elif token in [18]:
                self.state = 119
                self.match(PhiSQLParser.FPE)
                self.state = 120
                self.match(PhiSQLParser.KEY)
                self.state = 121
                self.match(PhiSQLParser.FROM)
                self.state = 122
                self.match(PhiSQLParser.ENV)
                self.state = 123
                localctx.fpeKeyEnv = self.match(PhiSQLParser.STRING_LITERAL)
                self.state = 124
                self.match(PhiSQLParser.TWEAK)
                self.state = 125
                self.match(PhiSQLParser.FROM)
                self.state = 126
                self.match(PhiSQLParser.ENV)
                self.state = 127
                localctx.fpeTweakEnv = self.match(PhiSQLParser.STRING_LITERAL)
                pass
            elif token in [23, 24, 25, 26]:
                self.state = 128
                localctx.configBlock = self._input.LT(1)
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 125829120) != 0)):
                    localctx.configBlock = self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 129
                self.match(PhiSQLParser.T__1)
                self.state = 130
                self.settingList()
                self.state = 131
                self.match(PhiSQLParser.T__2)
                pass
            elif token in [27]:
                self.state = 133
                self.match(PhiSQLParser.GRAPHICAL)
                self.state = 134
                self.match(PhiSQLParser.BOX)
                self.state = 135
                self.match(PhiSQLParser.T__1)
                self.state = 136
                self.settingList()
                self.state = 137
                self.match(PhiSQLParser.T__2)
                pass
            elif token in [91]:
                self.state = 139
                localctx.blockName = self.match(PhiSQLParser.ID)
                self.state = 141
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==91:
                    self.state = 140
                    localctx.subName = self.match(PhiSQLParser.ID)


                self.state = 143
                self.match(PhiSQLParser.T__1)
                self.state = 144
                self.settingList()
                self.state = 145
                self.match(PhiSQLParser.T__2)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SettingListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def setting(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PhiSQLParser.SettingContext)
            else:
                return self.getTypedRuleContext(PhiSQLParser.SettingContext,i)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_settingList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSettingList" ):
                listener.enterSettingList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSettingList" ):
                listener.exitSettingList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSettingList" ):
                return visitor.visitSettingList(self)
            else:
                return visitor.visitChildren(self)




    def settingList(self):

        localctx = PhiSQLParser.SettingListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_settingList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 149
            self.setting()
            self.state = 154
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4:
                self.state = 150
                self.match(PhiSQLParser.T__3)
                self.state = 151
                self.setting()
                self.state = 156
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SettingContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def settingKey(self):
            return self.getTypedRuleContext(PhiSQLParser.SettingKeyContext,0)


        def settingValue(self):
            return self.getTypedRuleContext(PhiSQLParser.SettingValueContext,0)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_setting

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSetting" ):
                listener.enterSetting(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSetting" ):
                listener.exitSetting(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSetting" ):
                return visitor.visitSetting(self)
            else:
                return visitor.visitChildren(self)




    def setting(self):

        localctx = PhiSQLParser.SettingContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_setting)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 157
            self.settingKey()
            self.state = 158
            self.match(PhiSQLParser.T__4)
            self.state = 159
            self.settingValue()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SettingKeyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(PhiSQLParser.ID, 0)

        def STRING_LITERAL(self):
            return self.getToken(PhiSQLParser.STRING_LITERAL, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_settingKey

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSettingKey" ):
                listener.enterSettingKey(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSettingKey" ):
                listener.exitSettingKey(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSettingKey" ):
                return visitor.visitSettingKey(self)
            else:
                return visitor.visitChildren(self)




    def settingKey(self):

        localctx = PhiSQLParser.SettingKeyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_settingKey)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 161
            _la = self._input.LA(1)
            if not(_la==91 or _la==92):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SettingValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def literal(self):
            return self.getTypedRuleContext(PhiSQLParser.LiteralContext,0)


        def objectValue(self):
            return self.getTypedRuleContext(PhiSQLParser.ObjectValueContext,0)


        def arrayValue(self):
            return self.getTypedRuleContext(PhiSQLParser.ArrayValueContext,0)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_settingValue

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSettingValue" ):
                listener.enterSettingValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSettingValue" ):
                listener.exitSettingValue(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSettingValue" ):
                return visitor.visitSettingValue(self)
            else:
                return visitor.visitChildren(self)




    def settingValue(self):

        localctx = PhiSQLParser.SettingValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_settingValue)
        try:
            self.state = 166
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [90, 91, 92, 93]:
                self.enterOuterAlt(localctx, 1)
                self.state = 163
                self.literal()
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 2)
                self.state = 164
                self.objectValue()
                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 3)
                self.state = 165
                self.arrayValue()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ObjectValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def settingList(self):
            return self.getTypedRuleContext(PhiSQLParser.SettingListContext,0)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_objectValue

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterObjectValue" ):
                listener.enterObjectValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitObjectValue" ):
                listener.exitObjectValue(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitObjectValue" ):
                return visitor.visitObjectValue(self)
            else:
                return visitor.visitChildren(self)




    def objectValue(self):

        localctx = PhiSQLParser.ObjectValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_objectValue)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 168
            self.match(PhiSQLParser.T__1)
            self.state = 169
            self.settingList()
            self.state = 170
            self.match(PhiSQLParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArrayValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def settingValue(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PhiSQLParser.SettingValueContext)
            else:
                return self.getTypedRuleContext(PhiSQLParser.SettingValueContext,i)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_arrayValue

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArrayValue" ):
                listener.enterArrayValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArrayValue" ):
                listener.exitArrayValue(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArrayValue" ):
                return visitor.visitArrayValue(self)
            else:
                return visitor.visitChildren(self)




    def arrayValue(self):

        localctx = PhiSQLParser.ArrayValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_arrayValue)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 172
            self.match(PhiSQLParser.T__5)
            self.state = 181
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2 or _la==6 or ((((_la - 90)) & ~0x3f) == 0 and ((1 << (_la - 90)) & 15) != 0):
                self.state = 173
                self.settingValue()
                self.state = 178
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==4:
                    self.state = 174
                    self.match(PhiSQLParser.T__3)
                    self.state = 175
                    self.settingValue()
                    self.state = 180
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 183
            self.match(PhiSQLParser.T__6)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OptionsClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OPTIONS(self):
            return self.getToken(PhiSQLParser.OPTIONS, 0)

        def settingList(self):
            return self.getTypedRuleContext(PhiSQLParser.SettingListContext,0)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_optionsClause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOptionsClause" ):
                listener.enterOptionsClause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOptionsClause" ):
                listener.exitOptionsClause(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOptionsClause" ):
                return visitor.visitOptionsClause(self)
            else:
                return visitor.visitChildren(self)




    def optionsClause(self):

        localctx = PhiSQLParser.OptionsClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_optionsClause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 185
            self.match(PhiSQLParser.OPTIONS)
            self.state = 186
            self.match(PhiSQLParser.T__1)
            self.state = 187
            self.settingList()
            self.state = 188
            self.match(PhiSQLParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RedactStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def REDACT(self):
            return self.getToken(PhiSQLParser.REDACT, 0)

        def entityList(self):
            return self.getTypedRuleContext(PhiSQLParser.EntityListContext,0)


        def WITH(self):
            return self.getToken(PhiSQLParser.WITH, 0)

        def strategyExpr(self):
            return self.getTypedRuleContext(PhiSQLParser.StrategyExprContext,0)


        def WHERE(self):
            return self.getToken(PhiSQLParser.WHERE, 0)

        def predicate(self):
            return self.getTypedRuleContext(PhiSQLParser.PredicateContext,0)


        def optionsClause(self):
            return self.getTypedRuleContext(PhiSQLParser.OptionsClauseContext,0)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_redactStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRedactStmt" ):
                listener.enterRedactStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRedactStmt" ):
                listener.exitRedactStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRedactStmt" ):
                return visitor.visitRedactStmt(self)
            else:
                return visitor.visitChildren(self)




    def redactStmt(self):

        localctx = PhiSQLParser.RedactStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_redactStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 190
            self.match(PhiSQLParser.REDACT)
            self.state = 191
            self.entityList()
            self.state = 194
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==35:
                self.state = 192
                self.match(PhiSQLParser.WITH)
                self.state = 193
                self.strategyExpr()


            self.state = 198
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 196
                self.match(PhiSQLParser.WHERE)
                self.state = 197
                self.predicate(0)


            self.state = 201
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 200
                self.optionsClause()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DeidentifyStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DEIDENTIFY(self):
            return self.getToken(PhiSQLParser.DEIDENTIFY, 0)

        def entityAssignment(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PhiSQLParser.EntityAssignmentContext)
            else:
                return self.getTypedRuleContext(PhiSQLParser.EntityAssignmentContext,i)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_deidentifyStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDeidentifyStmt" ):
                listener.enterDeidentifyStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDeidentifyStmt" ):
                listener.exitDeidentifyStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDeidentifyStmt" ):
                return visitor.visitDeidentifyStmt(self)
            else:
                return visitor.visitChildren(self)




    def deidentifyStmt(self):

        localctx = PhiSQLParser.DeidentifyStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_deidentifyStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 203
            self.match(PhiSQLParser.DEIDENTIFY)
            self.state = 204
            self.entityAssignment()
            self.state = 209
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4:
                self.state = 205
                self.match(PhiSQLParser.T__3)
                self.state = 206
                self.entityAssignment()
                self.state = 211
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EntityAssignmentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def entityType(self):
            return self.getTypedRuleContext(PhiSQLParser.EntityTypeContext,0)


        def AS(self):
            return self.getToken(PhiSQLParser.AS, 0)

        def strategyExpr(self):
            return self.getTypedRuleContext(PhiSQLParser.StrategyExprContext,0)


        def optionsClause(self):
            return self.getTypedRuleContext(PhiSQLParser.OptionsClauseContext,0)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_entityAssignment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEntityAssignment" ):
                listener.enterEntityAssignment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEntityAssignment" ):
                listener.exitEntityAssignment(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEntityAssignment" ):
                return visitor.visitEntityAssignment(self)
            else:
                return visitor.visitChildren(self)




    def entityAssignment(self):

        localctx = PhiSQLParser.EntityAssignmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_entityAssignment)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 212
            self.entityType()
            self.state = 213
            self.match(PhiSQLParser.AS)
            self.state = 214
            self.strategyExpr()
            self.state = 216
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 215
                self.optionsClause()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IgnoreStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IGNORE(self):
            return self.getToken(PhiSQLParser.IGNORE, 0)

        def TERMS(self):
            return self.getToken(PhiSQLParser.TERMS, 0)

        def stringList(self):
            return self.getTypedRuleContext(PhiSQLParser.StringListContext,0)


        def PATTERN(self):
            return self.getToken(PhiSQLParser.PATTERN, 0)

        def STRING_LITERAL(self):
            return self.getToken(PhiSQLParser.STRING_LITERAL, 0)

        def FOR(self):
            return self.getToken(PhiSQLParser.FOR, 0)

        def entityList(self):
            return self.getTypedRuleContext(PhiSQLParser.EntityListContext,0)


        def optionsClause(self):
            return self.getTypedRuleContext(PhiSQLParser.OptionsClauseContext,0)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_ignoreStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIgnoreStmt" ):
                listener.enterIgnoreStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIgnoreStmt" ):
                listener.exitIgnoreStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIgnoreStmt" ):
                return visitor.visitIgnoreStmt(self)
            else:
                return visitor.visitChildren(self)




    def ignoreStmt(self):

        localctx = PhiSQLParser.IgnoreStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_ignoreStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 218
            self.match(PhiSQLParser.IGNORE)
            self.state = 223
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [32]:
                self.state = 219
                self.match(PhiSQLParser.TERMS)
                self.state = 220
                self.stringList()
                pass
            elif token in [33]:
                self.state = 221
                self.match(PhiSQLParser.PATTERN)
                self.state = 222
                self.match(PhiSQLParser.STRING_LITERAL)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 227
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==34:
                self.state = 225
                self.match(PhiSQLParser.FOR)
                self.state = 226
                self.entityList()


            self.state = 230
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 229
                self.optionsClause()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DefineIdentifierStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.classification = None # Token
            self.pattern = None # Token
            self.groupNumber = None # Token
            self.sensitivity = None # Token

        def DEFINE(self):
            return self.getToken(PhiSQLParser.DEFINE, 0)

        def IDENTIFIER_KW(self):
            return self.getToken(PhiSQLParser.IDENTIFIER_KW, 0)

        def MATCHING(self):
            return self.getToken(PhiSQLParser.MATCHING, 0)

        def WITH(self):
            return self.getToken(PhiSQLParser.WITH, 0)

        def strategyExpr(self):
            return self.getTypedRuleContext(PhiSQLParser.StrategyExprContext,0)


        def STRING_LITERAL(self, i:int=None):
            if i is None:
                return self.getTokens(PhiSQLParser.STRING_LITERAL)
            else:
                return self.getToken(PhiSQLParser.STRING_LITERAL, i)

        def GROUP(self):
            return self.getToken(PhiSQLParser.GROUP, 0)

        def CASE(self):
            return self.getToken(PhiSQLParser.CASE, 0)

        def WHERE(self):
            return self.getToken(PhiSQLParser.WHERE, 0)

        def predicate(self):
            return self.getTypedRuleContext(PhiSQLParser.PredicateContext,0)


        def optionsClause(self):
            return self.getTypedRuleContext(PhiSQLParser.OptionsClauseContext,0)


        def NUMERIC_LITERAL(self):
            return self.getToken(PhiSQLParser.NUMERIC_LITERAL, 0)

        def SENSITIVE(self):
            return self.getToken(PhiSQLParser.SENSITIVE, 0)

        def INSENSITIVE(self):
            return self.getToken(PhiSQLParser.INSENSITIVE, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_defineIdentifierStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDefineIdentifierStmt" ):
                listener.enterDefineIdentifierStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDefineIdentifierStmt" ):
                listener.exitDefineIdentifierStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDefineIdentifierStmt" ):
                return visitor.visitDefineIdentifierStmt(self)
            else:
                return visitor.visitChildren(self)




    def defineIdentifierStmt(self):

        localctx = PhiSQLParser.DefineIdentifierStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_defineIdentifierStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 232
            self.match(PhiSQLParser.DEFINE)
            self.state = 233
            self.match(PhiSQLParser.IDENTIFIER_KW)
            self.state = 234
            localctx.classification = self.match(PhiSQLParser.STRING_LITERAL)
            self.state = 235
            self.match(PhiSQLParser.MATCHING)
            self.state = 236
            localctx.pattern = self.match(PhiSQLParser.STRING_LITERAL)
            self.state = 239
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==43:
                self.state = 237
                self.match(PhiSQLParser.GROUP)
                self.state = 238
                localctx.groupNumber = self.match(PhiSQLParser.NUMERIC_LITERAL)


            self.state = 243
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==44:
                self.state = 241
                self.match(PhiSQLParser.CASE)
                self.state = 242
                localctx.sensitivity = self._input.LT(1)
                _la = self._input.LA(1)
                if not(_la==45 or _la==46):
                    localctx.sensitivity = self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


            self.state = 245
            self.match(PhiSQLParser.WITH)
            self.state = 246
            self.strategyExpr()
            self.state = 249
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 247
                self.match(PhiSQLParser.WHERE)
                self.state = 248
                self.predicate(0)


            self.state = 252
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 251
                self.optionsClause()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DefineDictionaryStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.classification = None # Token
            self.sensitivity = None # Token
            self.capitalized = None # Token

        def DEFINE(self):
            return self.getToken(PhiSQLParser.DEFINE, 0)

        def DICTIONARY(self):
            return self.getToken(PhiSQLParser.DICTIONARY, 0)

        def TERMS(self):
            return self.getToken(PhiSQLParser.TERMS, 0)

        def stringList(self):
            return self.getTypedRuleContext(PhiSQLParser.StringListContext,0)


        def WITH(self):
            return self.getToken(PhiSQLParser.WITH, 0)

        def strategyExpr(self):
            return self.getTypedRuleContext(PhiSQLParser.StrategyExprContext,0)


        def STRING_LITERAL(self):
            return self.getToken(PhiSQLParser.STRING_LITERAL, 0)

        def FUZZY(self):
            return self.getToken(PhiSQLParser.FUZZY, 0)

        def optionsClause(self):
            return self.getTypedRuleContext(PhiSQLParser.OptionsClauseContext,0)


        def CAPITALIZED(self):
            return self.getToken(PhiSQLParser.CAPITALIZED, 0)

        def SENSITIVITY(self):
            return self.getToken(PhiSQLParser.SENSITIVITY, 0)

        def ID(self):
            return self.getToken(PhiSQLParser.ID, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_defineDictionaryStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDefineDictionaryStmt" ):
                listener.enterDefineDictionaryStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDefineDictionaryStmt" ):
                listener.exitDefineDictionaryStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDefineDictionaryStmt" ):
                return visitor.visitDefineDictionaryStmt(self)
            else:
                return visitor.visitChildren(self)




    def defineDictionaryStmt(self):

        localctx = PhiSQLParser.DefineDictionaryStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_defineDictionaryStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 254
            self.match(PhiSQLParser.DEFINE)
            self.state = 255
            self.match(PhiSQLParser.DICTIONARY)
            self.state = 256
            localctx.classification = self.match(PhiSQLParser.STRING_LITERAL)
            self.state = 257
            self.match(PhiSQLParser.TERMS)
            self.state = 258
            self.stringList()
            self.state = 264
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==51:
                self.state = 259
                self.match(PhiSQLParser.FUZZY)
                self.state = 262
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==52:
                    self.state = 260
                    self.match(PhiSQLParser.SENSITIVITY)
                    self.state = 261
                    localctx.sensitivity = self.match(PhiSQLParser.ID)




            self.state = 267
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==53:
                self.state = 266
                localctx.capitalized = self.match(PhiSQLParser.CAPITALIZED)


            self.state = 269
            self.match(PhiSQLParser.WITH)
            self.state = 270
            self.strategyExpr()
            self.state = 272
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 271
                self.optionsClause()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DefineSectionStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.startPattern = None # Token
            self.endPattern = None # Token

        def DEFINE(self):
            return self.getToken(PhiSQLParser.DEFINE, 0)

        def SECTION(self):
            return self.getToken(PhiSQLParser.SECTION, 0)

        def START(self):
            return self.getToken(PhiSQLParser.START, 0)

        def END(self):
            return self.getToken(PhiSQLParser.END, 0)

        def WITH(self):
            return self.getToken(PhiSQLParser.WITH, 0)

        def strategyExpr(self):
            return self.getTypedRuleContext(PhiSQLParser.StrategyExprContext,0)


        def STRING_LITERAL(self, i:int=None):
            if i is None:
                return self.getTokens(PhiSQLParser.STRING_LITERAL)
            else:
                return self.getToken(PhiSQLParser.STRING_LITERAL, i)

        def optionsClause(self):
            return self.getTypedRuleContext(PhiSQLParser.OptionsClauseContext,0)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_defineSectionStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDefineSectionStmt" ):
                listener.enterDefineSectionStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDefineSectionStmt" ):
                listener.exitDefineSectionStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDefineSectionStmt" ):
                return visitor.visitDefineSectionStmt(self)
            else:
                return visitor.visitChildren(self)




    def defineSectionStmt(self):

        localctx = PhiSQLParser.DefineSectionStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_defineSectionStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 274
            self.match(PhiSQLParser.DEFINE)
            self.state = 275
            self.match(PhiSQLParser.SECTION)
            self.state = 276
            self.match(PhiSQLParser.START)
            self.state = 277
            localctx.startPattern = self.match(PhiSQLParser.STRING_LITERAL)
            self.state = 278
            self.match(PhiSQLParser.END)
            self.state = 279
            localctx.endPattern = self.match(PhiSQLParser.STRING_LITERAL)
            self.state = 280
            self.match(PhiSQLParser.WITH)
            self.state = 281
            self.strategyExpr()
            self.state = 283
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 282
                self.optionsClause()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DefineGeneratorStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.generatorName = None # Token
            self.generatorType = None # Token

        def DEFINE(self):
            return self.getToken(PhiSQLParser.DEFINE, 0)

        def GENERATOR(self):
            return self.getToken(PhiSQLParser.GENERATOR, 0)

        def TYPE(self):
            return self.getToken(PhiSQLParser.TYPE, 0)

        def optionsClause(self):
            return self.getTypedRuleContext(PhiSQLParser.OptionsClauseContext,0)


        def STRING_LITERAL(self, i:int=None):
            if i is None:
                return self.getTokens(PhiSQLParser.STRING_LITERAL)
            else:
                return self.getToken(PhiSQLParser.STRING_LITERAL, i)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_defineGeneratorStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDefineGeneratorStmt" ):
                listener.enterDefineGeneratorStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDefineGeneratorStmt" ):
                listener.exitDefineGeneratorStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDefineGeneratorStmt" ):
                return visitor.visitDefineGeneratorStmt(self)
            else:
                return visitor.visitChildren(self)




    def defineGeneratorStmt(self):

        localctx = PhiSQLParser.DefineGeneratorStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_defineGeneratorStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 285
            self.match(PhiSQLParser.DEFINE)
            self.state = 286
            self.match(PhiSQLParser.GENERATOR)
            self.state = 287
            localctx.generatorName = self.match(PhiSQLParser.STRING_LITERAL)
            self.state = 288
            self.match(PhiSQLParser.TYPE)
            self.state = 289
            localctx.generatorType = self.match(PhiSQLParser.STRING_LITERAL)
            self.state = 290
            self.optionsClause()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DetectStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.endpoint = None # Token
            self.model = None # Token

        def DETECT(self):
            return self.getToken(PhiSQLParser.DETECT, 0)

        def PHEYE(self):
            return self.getToken(PhiSQLParser.PHEYE, 0)

        def WITH(self):
            return self.getToken(PhiSQLParser.WITH, 0)

        def strategyExpr(self):
            return self.getTypedRuleContext(PhiSQLParser.StrategyExprContext,0)


        def LABELS(self):
            return self.getToken(PhiSQLParser.LABELS, 0)

        def stringList(self):
            return self.getTypedRuleContext(PhiSQLParser.StringListContext,0)


        def ENDPOINT(self):
            return self.getToken(PhiSQLParser.ENDPOINT, 0)

        def MODEL(self):
            return self.getToken(PhiSQLParser.MODEL, 0)

        def WHERE(self):
            return self.getToken(PhiSQLParser.WHERE, 0)

        def predicate(self):
            return self.getTypedRuleContext(PhiSQLParser.PredicateContext,0)


        def optionsClause(self):
            return self.getTypedRuleContext(PhiSQLParser.OptionsClauseContext,0)


        def STRING_LITERAL(self, i:int=None):
            if i is None:
                return self.getTokens(PhiSQLParser.STRING_LITERAL)
            else:
                return self.getToken(PhiSQLParser.STRING_LITERAL, i)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_detectStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDetectStmt" ):
                listener.enterDetectStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDetectStmt" ):
                listener.exitDetectStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDetectStmt" ):
                return visitor.visitDetectStmt(self)
            else:
                return visitor.visitChildren(self)




    def detectStmt(self):

        localctx = PhiSQLParser.DetectStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_detectStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 292
            self.match(PhiSQLParser.DETECT)
            self.state = 293
            self.match(PhiSQLParser.PHEYE)
            self.state = 296
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==59:
                self.state = 294
                self.match(PhiSQLParser.LABELS)
                self.state = 295
                self.stringList()


            self.state = 300
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==60:
                self.state = 298
                self.match(PhiSQLParser.ENDPOINT)
                self.state = 299
                localctx.endpoint = self.match(PhiSQLParser.STRING_LITERAL)


            self.state = 304
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==61:
                self.state = 302
                self.match(PhiSQLParser.MODEL)
                self.state = 303
                localctx.model = self.match(PhiSQLParser.STRING_LITERAL)


            self.state = 306
            self.match(PhiSQLParser.WITH)
            self.state = 307
            self.strategyExpr()
            self.state = 310
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 308
                self.match(PhiSQLParser.WHERE)
                self.state = 309
                self.predicate(0)


            self.state = 313
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==56:
                self.state = 312
                self.optionsClause()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DiscoveryStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return PhiSQLParser.RULE_discoveryStmt

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class SelectFindingsStmtContext(DiscoveryStmtContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.DiscoveryStmtContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def SELECT(self):
            return self.getToken(PhiSQLParser.SELECT, 0)
        def projectionList(self):
            return self.getTypedRuleContext(PhiSQLParser.ProjectionListContext,0)

        def FROM(self):
            return self.getToken(PhiSQLParser.FROM, 0)
        def findingsRef(self):
            return self.getTypedRuleContext(PhiSQLParser.FindingsRefContext,0)

        def whereDiscovery(self):
            return self.getTypedRuleContext(PhiSQLParser.WhereDiscoveryContext,0)

        def groupByClause(self):
            return self.getTypedRuleContext(PhiSQLParser.GroupByClauseContext,0)

        def limitClause(self):
            return self.getTypedRuleContext(PhiSQLParser.LimitClauseContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSelectFindingsStmt" ):
                listener.enterSelectFindingsStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSelectFindingsStmt" ):
                listener.exitSelectFindingsStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSelectFindingsStmt" ):
                return visitor.visitSelectFindingsStmt(self)
            else:
                return visitor.visitChildren(self)


    class FindPiiStmtContext(DiscoveryStmtContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.DiscoveryStmtContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def FIND(self):
            return self.getToken(PhiSQLParser.FIND, 0)
        def PII(self):
            return self.getToken(PhiSQLParser.PII, 0)
        def inClause(self):
            return self.getTypedRuleContext(PhiSQLParser.InClauseContext,0)

        def whereDiscovery(self):
            return self.getTypedRuleContext(PhiSQLParser.WhereDiscoveryContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFindPiiStmt" ):
                listener.enterFindPiiStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFindPiiStmt" ):
                listener.exitFindPiiStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFindPiiStmt" ):
                return visitor.visitFindPiiStmt(self)
            else:
                return visitor.visitChildren(self)


    class DiscoverEntitiesStmtContext(DiscoveryStmtContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.DiscoveryStmtContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def DISCOVER(self):
            return self.getToken(PhiSQLParser.DISCOVER, 0)
        def ENTITIES(self):
            return self.getToken(PhiSQLParser.ENTITIES, 0)
        def inClause(self):
            return self.getTypedRuleContext(PhiSQLParser.InClauseContext,0)

        def whereDiscovery(self):
            return self.getTypedRuleContext(PhiSQLParser.WhereDiscoveryContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDiscoverEntitiesStmt" ):
                listener.enterDiscoverEntitiesStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDiscoverEntitiesStmt" ):
                listener.exitDiscoverEntitiesStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDiscoverEntitiesStmt" ):
                return visitor.visitDiscoverEntitiesStmt(self)
            else:
                return visitor.visitChildren(self)


    class ScanStmtContext(DiscoveryStmtContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.DiscoveryStmtContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def SCAN(self):
            return self.getToken(PhiSQLParser.SCAN, 0)
        def inClause(self):
            return self.getTypedRuleContext(PhiSQLParser.InClauseContext,0)

        def whereDiscovery(self):
            return self.getTypedRuleContext(PhiSQLParser.WhereDiscoveryContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterScanStmt" ):
                listener.enterScanStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitScanStmt" ):
                listener.exitScanStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitScanStmt" ):
                return visitor.visitScanStmt(self)
            else:
                return visitor.visitChildren(self)



    def discoveryStmt(self):

        localctx = PhiSQLParser.DiscoveryStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_discoveryStmt)
        self._la = 0 # Token type
        try:
            self.state = 345
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [62]:
                localctx = PhiSQLParser.FindPiiStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 315
                self.match(PhiSQLParser.FIND)
                self.state = 316
                self.match(PhiSQLParser.PII)
                self.state = 317
                self.inClause()
                self.state = 319
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==36:
                    self.state = 318
                    self.whereDiscovery()


                pass
            elif token in [64]:
                localctx = PhiSQLParser.DiscoverEntitiesStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 321
                self.match(PhiSQLParser.DISCOVER)
                self.state = 322
                self.match(PhiSQLParser.ENTITIES)
                self.state = 323
                self.inClause()
                self.state = 325
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==36:
                    self.state = 324
                    self.whereDiscovery()


                pass
            elif token in [66]:
                localctx = PhiSQLParser.ScanStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 327
                self.match(PhiSQLParser.SCAN)
                self.state = 328
                self.inClause()
                self.state = 330
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==36:
                    self.state = 329
                    self.whereDiscovery()


                pass
            elif token in [68]:
                localctx = PhiSQLParser.SelectFindingsStmtContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 332
                self.match(PhiSQLParser.SELECT)
                self.state = 333
                self.projectionList()
                self.state = 334
                self.match(PhiSQLParser.FROM)
                self.state = 335
                self.findingsRef()
                self.state = 337
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==36:
                    self.state = 336
                    self.whereDiscovery()


                self.state = 340
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==43:
                    self.state = 339
                    self.groupByClause()


                self.state = 343
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==70:
                    self.state = 342
                    self.limitClause()


                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class InClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.uri = None # Token

        def IN(self):
            return self.getToken(PhiSQLParser.IN, 0)

        def STRING_LITERAL(self):
            return self.getToken(PhiSQLParser.STRING_LITERAL, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_inClause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInClause" ):
                listener.enterInClause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInClause" ):
                listener.exitInClause(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInClause" ):
                return visitor.visitInClause(self)
            else:
                return visitor.visitChildren(self)




    def inClause(self):

        localctx = PhiSQLParser.InClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_inClause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 347
            self.match(PhiSQLParser.IN)
            self.state = 348
            localctx.uri = self.match(PhiSQLParser.STRING_LITERAL)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WhereDiscoveryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHERE(self):
            return self.getToken(PhiSQLParser.WHERE, 0)

        def discoveryPredicate(self):
            return self.getTypedRuleContext(PhiSQLParser.DiscoveryPredicateContext,0)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_whereDiscovery

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWhereDiscovery" ):
                listener.enterWhereDiscovery(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWhereDiscovery" ):
                listener.exitWhereDiscovery(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWhereDiscovery" ):
                return visitor.visitWhereDiscovery(self)
            else:
                return visitor.visitChildren(self)




    def whereDiscovery(self):

        localctx = PhiSQLParser.WhereDiscoveryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_whereDiscovery)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 350
            self.match(PhiSQLParser.WHERE)
            self.state = 351
            self.discoveryPredicate(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DiscoveryPredicateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return PhiSQLParser.RULE_discoveryPredicate

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class ParenDiscoveryPredicateContext(DiscoveryPredicateContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.DiscoveryPredicateContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def discoveryPredicate(self):
            return self.getTypedRuleContext(PhiSQLParser.DiscoveryPredicateContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParenDiscoveryPredicate" ):
                listener.enterParenDiscoveryPredicate(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParenDiscoveryPredicate" ):
                listener.exitParenDiscoveryPredicate(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParenDiscoveryPredicate" ):
                return visitor.visitParenDiscoveryPredicate(self)
            else:
                return visitor.visitChildren(self)


    class InDiscoveryPredicateContext(DiscoveryPredicateContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.DiscoveryPredicateContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def columnRef(self):
            return self.getTypedRuleContext(PhiSQLParser.ColumnRefContext,0)

        def IN(self):
            return self.getToken(PhiSQLParser.IN, 0)
        def stringList(self):
            return self.getTypedRuleContext(PhiSQLParser.StringListContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInDiscoveryPredicate" ):
                listener.enterInDiscoveryPredicate(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInDiscoveryPredicate" ):
                listener.exitInDiscoveryPredicate(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInDiscoveryPredicate" ):
                return visitor.visitInDiscoveryPredicate(self)
            else:
                return visitor.visitChildren(self)


    class CompareDiscoveryPredicateContext(DiscoveryPredicateContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.DiscoveryPredicateContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def columnRef(self):
            return self.getTypedRuleContext(PhiSQLParser.ColumnRefContext,0)

        def compareOp(self):
            return self.getTypedRuleContext(PhiSQLParser.CompareOpContext,0)

        def STRING_LITERAL(self):
            return self.getToken(PhiSQLParser.STRING_LITERAL, 0)
        def NUMERIC_LITERAL(self):
            return self.getToken(PhiSQLParser.NUMERIC_LITERAL, 0)
        def BOOLEAN_LITERAL(self):
            return self.getToken(PhiSQLParser.BOOLEAN_LITERAL, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCompareDiscoveryPredicate" ):
                listener.enterCompareDiscoveryPredicate(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCompareDiscoveryPredicate" ):
                listener.exitCompareDiscoveryPredicate(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCompareDiscoveryPredicate" ):
                return visitor.visitCompareDiscoveryPredicate(self)
            else:
                return visitor.visitChildren(self)


    class LogicalDiscoveryPredicateContext(DiscoveryPredicateContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.DiscoveryPredicateContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def discoveryPredicate(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PhiSQLParser.DiscoveryPredicateContext)
            else:
                return self.getTypedRuleContext(PhiSQLParser.DiscoveryPredicateContext,i)

        def AND(self):
            return self.getToken(PhiSQLParser.AND, 0)
        def OR(self):
            return self.getToken(PhiSQLParser.OR, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalDiscoveryPredicate" ):
                listener.enterLogicalDiscoveryPredicate(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalDiscoveryPredicate" ):
                listener.exitLogicalDiscoveryPredicate(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalDiscoveryPredicate" ):
                return visitor.visitLogicalDiscoveryPredicate(self)
            else:
                return visitor.visitChildren(self)



    def discoveryPredicate(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = PhiSQLParser.DiscoveryPredicateContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 46
        self.enterRecursionRule(localctx, 46, self.RULE_discoveryPredicate, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 366
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,38,self._ctx)
            if la_ == 1:
                localctx = PhiSQLParser.InDiscoveryPredicateContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 354
                self.columnRef()
                self.state = 355
                self.match(PhiSQLParser.IN)
                self.state = 356
                self.stringList()
                pass

            elif la_ == 2:
                localctx = PhiSQLParser.CompareDiscoveryPredicateContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 358
                self.columnRef()
                self.state = 359
                self.compareOp()
                self.state = 360
                _la = self._input.LA(1)
                if not(((((_la - 90)) & ~0x3f) == 0 and ((1 << (_la - 90)) & 13) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass

            elif la_ == 3:
                localctx = PhiSQLParser.ParenDiscoveryPredicateContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 362
                self.match(PhiSQLParser.T__1)
                self.state = 363
                self.discoveryPredicate(0)
                self.state = 364
                self.match(PhiSQLParser.T__2)
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 373
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,39,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = PhiSQLParser.LogicalDiscoveryPredicateContext(self, PhiSQLParser.DiscoveryPredicateContext(self, _parentctx, _parentState))
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_discoveryPredicate)
                    self.state = 368
                    if not self.precpred(self._ctx, 1):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                    self.state = 369
                    _la = self._input.LA(1)
                    if not(_la==38 or _la==39):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 370
                    self.discoveryPredicate(2) 
                self.state = 375
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,39,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class ProjectionListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def projection(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PhiSQLParser.ProjectionContext)
            else:
                return self.getTypedRuleContext(PhiSQLParser.ProjectionContext,i)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_projectionList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProjectionList" ):
                listener.enterProjectionList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProjectionList" ):
                listener.exitProjectionList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProjectionList" ):
                return visitor.visitProjectionList(self)
            else:
                return visitor.visitChildren(self)




    def projectionList(self):

        localctx = PhiSQLParser.ProjectionListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_projectionList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 376
            self.projection()
            self.state = 381
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4:
                self.state = 377
                self.match(PhiSQLParser.T__3)
                self.state = 378
                self.projection()
                self.state = 383
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ProjectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return PhiSQLParser.RULE_projection

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class ColumnProjectionContext(ProjectionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.ProjectionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def columnRef(self):
            return self.getTypedRuleContext(PhiSQLParser.ColumnRefContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColumnProjection" ):
                listener.enterColumnProjection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColumnProjection" ):
                listener.exitColumnProjection(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnProjection" ):
                return visitor.visitColumnProjection(self)
            else:
                return visitor.visitChildren(self)


    class AggregateProjectionContext(ProjectionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.ProjectionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def aggregate(self):
            return self.getTypedRuleContext(PhiSQLParser.AggregateContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAggregateProjection" ):
                listener.enterAggregateProjection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAggregateProjection" ):
                listener.exitAggregateProjection(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAggregateProjection" ):
                return visitor.visitAggregateProjection(self)
            else:
                return visitor.visitChildren(self)


    class StarProjectionContext(ProjectionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.ProjectionContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStarProjection" ):
                listener.enterStarProjection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStarProjection" ):
                listener.exitStarProjection(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStarProjection" ):
                return visitor.visitStarProjection(self)
            else:
                return visitor.visitChildren(self)



    def projection(self):

        localctx = PhiSQLParser.ProjectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_projection)
        try:
            self.state = 387
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [8]:
                localctx = PhiSQLParser.StarProjectionContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 384
                self.match(PhiSQLParser.T__7)
                pass
            elif token in [71, 72, 73, 74, 75]:
                localctx = PhiSQLParser.AggregateProjectionContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 385
                self.aggregate()
                pass
            elif token in [40, 91]:
                localctx = PhiSQLParser.ColumnProjectionContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 386
                self.columnRef()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AggregateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.aggFn = None # Token

        def aggArg(self):
            return self.getTypedRuleContext(PhiSQLParser.AggArgContext,0)


        def COUNT(self):
            return self.getToken(PhiSQLParser.COUNT, 0)

        def AVG(self):
            return self.getToken(PhiSQLParser.AVG, 0)

        def SUM(self):
            return self.getToken(PhiSQLParser.SUM, 0)

        def MIN(self):
            return self.getToken(PhiSQLParser.MIN, 0)

        def MAX(self):
            return self.getToken(PhiSQLParser.MAX, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_aggregate

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAggregate" ):
                listener.enterAggregate(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAggregate" ):
                listener.exitAggregate(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAggregate" ):
                return visitor.visitAggregate(self)
            else:
                return visitor.visitChildren(self)




    def aggregate(self):

        localctx = PhiSQLParser.AggregateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_aggregate)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 389
            localctx.aggFn = self._input.LT(1)
            _la = self._input.LA(1)
            if not(((((_la - 71)) & ~0x3f) == 0 and ((1 << (_la - 71)) & 31) != 0)):
                localctx.aggFn = self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 390
            self.match(PhiSQLParser.T__1)
            self.state = 391
            self.aggArg()
            self.state = 392
            self.match(PhiSQLParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AggArgContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return PhiSQLParser.RULE_aggArg

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class StarAggArgContext(AggArgContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.AggArgContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStarAggArg" ):
                listener.enterStarAggArg(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStarAggArg" ):
                listener.exitStarAggArg(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStarAggArg" ):
                return visitor.visitStarAggArg(self)
            else:
                return visitor.visitChildren(self)


    class ColumnAggArgContext(AggArgContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.AggArgContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def columnRef(self):
            return self.getTypedRuleContext(PhiSQLParser.ColumnRefContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColumnAggArg" ):
                listener.enterColumnAggArg(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColumnAggArg" ):
                listener.exitColumnAggArg(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnAggArg" ):
                return visitor.visitColumnAggArg(self)
            else:
                return visitor.visitChildren(self)



    def aggArg(self):

        localctx = PhiSQLParser.AggArgContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_aggArg)
        try:
            self.state = 396
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [8]:
                localctx = PhiSQLParser.StarAggArgContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 394
                self.match(PhiSQLParser.T__7)
                pass
            elif token in [40, 91]:
                localctx = PhiSQLParser.ColumnAggArgContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 395
                self.columnRef()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnRefContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(PhiSQLParser.ID, 0)

        def CONFIDENCE(self):
            return self.getToken(PhiSQLParser.CONFIDENCE, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_columnRef

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColumnRef" ):
                listener.enterColumnRef(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColumnRef" ):
                listener.exitColumnRef(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnRef" ):
                return visitor.visitColumnRef(self)
            else:
                return visitor.visitChildren(self)




    def columnRef(self):

        localctx = PhiSQLParser.ColumnRefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_columnRef)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 398
            _la = self._input.LA(1)
            if not(_la==40 or _la==91):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FindingsRefContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.namespace = None # Token
            self.table = None # Token

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(PhiSQLParser.ID)
            else:
                return self.getToken(PhiSQLParser.ID, i)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_findingsRef

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFindingsRef" ):
                listener.enterFindingsRef(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFindingsRef" ):
                listener.exitFindingsRef(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFindingsRef" ):
                return visitor.visitFindingsRef(self)
            else:
                return visitor.visitChildren(self)




    def findingsRef(self):

        localctx = PhiSQLParser.FindingsRefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_findingsRef)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 402
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,43,self._ctx)
            if la_ == 1:
                self.state = 400
                localctx.namespace = self.match(PhiSQLParser.ID)
                self.state = 401
                self.match(PhiSQLParser.T__8)


            self.state = 404
            localctx.table = self.match(PhiSQLParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GroupByClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def GROUP(self):
            return self.getToken(PhiSQLParser.GROUP, 0)

        def BY(self):
            return self.getToken(PhiSQLParser.BY, 0)

        def columnRef(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PhiSQLParser.ColumnRefContext)
            else:
                return self.getTypedRuleContext(PhiSQLParser.ColumnRefContext,i)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_groupByClause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGroupByClause" ):
                listener.enterGroupByClause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGroupByClause" ):
                listener.exitGroupByClause(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitGroupByClause" ):
                return visitor.visitGroupByClause(self)
            else:
                return visitor.visitChildren(self)




    def groupByClause(self):

        localctx = PhiSQLParser.GroupByClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_groupByClause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 406
            self.match(PhiSQLParser.GROUP)
            self.state = 407
            self.match(PhiSQLParser.BY)
            self.state = 408
            self.columnRef()
            self.state = 413
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4:
                self.state = 409
                self.match(PhiSQLParser.T__3)
                self.state = 410
                self.columnRef()
                self.state = 415
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LimitClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LIMIT(self):
            return self.getToken(PhiSQLParser.LIMIT, 0)

        def NUMERIC_LITERAL(self):
            return self.getToken(PhiSQLParser.NUMERIC_LITERAL, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_limitClause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLimitClause" ):
                listener.enterLimitClause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLimitClause" ):
                listener.exitLimitClause(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLimitClause" ):
                return visitor.visitLimitClause(self)
            else:
                return visitor.visitChildren(self)




    def limitClause(self):

        localctx = PhiSQLParser.LimitClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_limitClause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 416
            self.match(PhiSQLParser.LIMIT)
            self.state = 417
            self.match(PhiSQLParser.NUMERIC_LITERAL)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EntityListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def entityType(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PhiSQLParser.EntityTypeContext)
            else:
                return self.getTypedRuleContext(PhiSQLParser.EntityTypeContext,i)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_entityList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEntityList" ):
                listener.enterEntityList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEntityList" ):
                listener.exitEntityList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEntityList" ):
                return visitor.visitEntityList(self)
            else:
                return visitor.visitChildren(self)




    def entityList(self):

        localctx = PhiSQLParser.EntityListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_entityList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 419
            self.entityType()
            self.state = 424
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4:
                self.state = 420
                self.match(PhiSQLParser.T__3)
                self.state = 421
                self.entityType()
                self.state = 426
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EntityTypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return PhiSQLParser.RULE_entityType

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class CustomIdentifierContext(EntityTypeContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.EntityTypeContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def IDENTIFIER_KW(self):
            return self.getToken(PhiSQLParser.IDENTIFIER_KW, 0)
        def STRING_LITERAL(self):
            return self.getToken(PhiSQLParser.STRING_LITERAL, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCustomIdentifier" ):
                listener.enterCustomIdentifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCustomIdentifier" ):
                listener.exitCustomIdentifier(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCustomIdentifier" ):
                return visitor.visitCustomIdentifier(self)
            else:
                return visitor.visitChildren(self)


    class SimpleEntityTypeContext(EntityTypeContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.EntityTypeContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ID(self):
            return self.getToken(PhiSQLParser.ID, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSimpleEntityType" ):
                listener.enterSimpleEntityType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSimpleEntityType" ):
                listener.exitSimpleEntityType(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSimpleEntityType" ):
                return visitor.visitSimpleEntityType(self)
            else:
                return visitor.visitChildren(self)



    def entityType(self):

        localctx = PhiSQLParser.EntityTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_entityType)
        try:
            self.state = 432
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [91]:
                localctx = PhiSQLParser.SimpleEntityTypeContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 427
                self.match(PhiSQLParser.ID)
                pass
            elif token in [76]:
                localctx = PhiSQLParser.CustomIdentifierContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 428
                self.match(PhiSQLParser.IDENTIFIER_KW)
                self.state = 429
                self.match(PhiSQLParser.T__1)
                self.state = 430
                self.match(PhiSQLParser.STRING_LITERAL)
                self.state = 431
                self.match(PhiSQLParser.T__2)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StrategyExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def strategyName(self):
            return self.getTypedRuleContext(PhiSQLParser.StrategyNameContext,0)


        def strategyArgs(self):
            return self.getTypedRuleContext(PhiSQLParser.StrategyArgsContext,0)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_strategyExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStrategyExpr" ):
                listener.enterStrategyExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStrategyExpr" ):
                listener.exitStrategyExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStrategyExpr" ):
                return visitor.visitStrategyExpr(self)
            else:
                return visitor.visitChildren(self)




    def strategyExpr(self):

        localctx = PhiSQLParser.StrategyExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_strategyExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 434
            self.strategyName()
            self.state = 439
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 435
                self.match(PhiSQLParser.T__1)
                self.state = 436
                self.strategyArgs()
                self.state = 437
                self.match(PhiSQLParser.T__2)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StrategyNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def MASK(self):
            return self.getToken(PhiSQLParser.MASK, 0)

        def REDACT(self):
            return self.getToken(PhiSQLParser.REDACT, 0)

        def ENCRYPT(self):
            return self.getToken(PhiSQLParser.ENCRYPT, 0)

        def FPE_ENCRYPT(self):
            return self.getToken(PhiSQLParser.FPE_ENCRYPT, 0)

        def HASH_SHA256(self):
            return self.getToken(PhiSQLParser.HASH_SHA256, 0)

        def RANDOM_REPLACE(self):
            return self.getToken(PhiSQLParser.RANDOM_REPLACE, 0)

        def STATIC_REPLACE(self):
            return self.getToken(PhiSQLParser.STATIC_REPLACE, 0)

        def LAST_4(self):
            return self.getToken(PhiSQLParser.LAST_4, 0)

        def TRUNCATE(self):
            return self.getToken(PhiSQLParser.TRUNCATE, 0)

        def TRUNCATE_TO_YEAR(self):
            return self.getToken(PhiSQLParser.TRUNCATE_TO_YEAR, 0)

        def SHIFT(self):
            return self.getToken(PhiSQLParser.SHIFT, 0)

        def RELATIVE(self):
            return self.getToken(PhiSQLParser.RELATIVE, 0)

        def ABBREVIATE(self):
            return self.getToken(PhiSQLParser.ABBREVIATE, 0)

        def MAP_REPLACE(self):
            return self.getToken(PhiSQLParser.MAP_REPLACE, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_strategyName

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStrategyName" ):
                listener.enterStrategyName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStrategyName" ):
                listener.exitStrategyName(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStrategyName" ):
                return visitor.visitStrategyName(self)
            else:
                return visitor.visitChildren(self)




    def strategyName(self):

        localctx = PhiSQLParser.StrategyNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_strategyName)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 441
            _la = self._input.LA(1)
            if not(((((_la - 29)) & ~0x3f) == 0 and ((1 << (_la - 29)) & 2305561534236983297) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StrategyArgsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def namedArg(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PhiSQLParser.NamedArgContext)
            else:
                return self.getTypedRuleContext(PhiSQLParser.NamedArgContext,i)


        def getRuleIndex(self):
            return PhiSQLParser.RULE_strategyArgs

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStrategyArgs" ):
                listener.enterStrategyArgs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStrategyArgs" ):
                listener.exitStrategyArgs(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStrategyArgs" ):
                return visitor.visitStrategyArgs(self)
            else:
                return visitor.visitChildren(self)




    def strategyArgs(self):

        localctx = PhiSQLParser.StrategyArgsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_strategyArgs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 443
            self.namedArg()
            self.state = 448
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4:
                self.state = 444
                self.match(PhiSQLParser.T__3)
                self.state = 445
                self.namedArg()
                self.state = 450
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NamedArgContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.argName = None # Token

        def settingValue(self):
            return self.getTypedRuleContext(PhiSQLParser.SettingValueContext,0)


        def ID(self):
            return self.getToken(PhiSQLParser.ID, 0)

        def GENERATOR(self):
            return self.getToken(PhiSQLParser.GENERATOR, 0)

        def TYPE(self):
            return self.getToken(PhiSQLParser.TYPE, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_namedArg

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNamedArg" ):
                listener.enterNamedArg(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNamedArg" ):
                listener.exitNamedArg(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNamedArg" ):
                return visitor.visitNamedArg(self)
            else:
                return visitor.visitChildren(self)




    def namedArg(self):

        localctx = PhiSQLParser.NamedArgContext(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_namedArg)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 451
            localctx.argName = self._input.LT(1)
            _la = self._input.LA(1)
            if not(((((_la - 54)) & ~0x3f) == 0 and ((1 << (_la - 54)) & 137438953475) != 0)):
                localctx.argName = self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 452
            self.match(PhiSQLParser.T__4)
            self.state = 453
            self.settingValue()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PredicateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return PhiSQLParser.RULE_predicate

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class ConfidencePredicateContext(PredicateContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.PredicateContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def CONFIDENCE(self):
            return self.getToken(PhiSQLParser.CONFIDENCE, 0)
        def compareOp(self):
            return self.getTypedRuleContext(PhiSQLParser.CompareOpContext,0)

        def NUMERIC_LITERAL(self):
            return self.getToken(PhiSQLParser.NUMERIC_LITERAL, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterConfidencePredicate" ):
                listener.enterConfidencePredicate(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitConfidencePredicate" ):
                listener.exitConfidencePredicate(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConfidencePredicate" ):
                return visitor.visitConfidencePredicate(self)
            else:
                return visitor.visitChildren(self)


    class ParenPredicateContext(PredicateContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.PredicateContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def predicate(self):
            return self.getTypedRuleContext(PhiSQLParser.PredicateContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParenPredicate" ):
                listener.enterParenPredicate(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParenPredicate" ):
                listener.exitParenPredicate(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParenPredicate" ):
                return visitor.visitParenPredicate(self)
            else:
                return visitor.visitChildren(self)


    class LogicalPredicateContext(PredicateContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PhiSQLParser.PredicateContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def predicate(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PhiSQLParser.PredicateContext)
            else:
                return self.getTypedRuleContext(PhiSQLParser.PredicateContext,i)

        def AND(self):
            return self.getToken(PhiSQLParser.AND, 0)
        def OR(self):
            return self.getToken(PhiSQLParser.OR, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalPredicate" ):
                listener.enterLogicalPredicate(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalPredicate" ):
                listener.exitLogicalPredicate(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalPredicate" ):
                return visitor.visitLogicalPredicate(self)
            else:
                return visitor.visitChildren(self)



    def predicate(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = PhiSQLParser.PredicateContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 76
        self.enterRecursionRule(localctx, 76, self.RULE_predicate, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 464
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [40]:
                localctx = PhiSQLParser.ConfidencePredicateContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 456
                self.match(PhiSQLParser.CONFIDENCE)
                self.state = 457
                self.compareOp()
                self.state = 458
                self.match(PhiSQLParser.NUMERIC_LITERAL)
                pass
            elif token in [2]:
                localctx = PhiSQLParser.ParenPredicateContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 460
                self.match(PhiSQLParser.T__1)
                self.state = 461
                self.predicate(0)
                self.state = 462
                self.match(PhiSQLParser.T__2)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 471
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,50,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = PhiSQLParser.LogicalPredicateContext(self, PhiSQLParser.PredicateContext(self, _parentctx, _parentState))
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_predicate)
                    self.state = 466
                    if not self.precpred(self._ctx, 1):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                    self.state = 467
                    _la = self._input.LA(1)
                    if not(_la==38 or _la==39):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 468
                    self.predicate(2) 
                self.state = 473
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,50,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class CompareOpContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return PhiSQLParser.RULE_compareOp

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCompareOp" ):
                listener.enterCompareOp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCompareOp" ):
                listener.exitCompareOp(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCompareOp" ):
                return visitor.visitCompareOp(self)
            else:
                return visitor.visitChildren(self)




    def compareOp(self):

        localctx = PhiSQLParser.CompareOpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_compareOp)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 474
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 15392) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StringListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING_LITERAL(self, i:int=None):
            if i is None:
                return self.getTokens(PhiSQLParser.STRING_LITERAL)
            else:
                return self.getToken(PhiSQLParser.STRING_LITERAL, i)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_stringList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStringList" ):
                listener.enterStringList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStringList" ):
                listener.exitStringList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStringList" ):
                return visitor.visitStringList(self)
            else:
                return visitor.visitChildren(self)




    def stringList(self):

        localctx = PhiSQLParser.StringListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_stringList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 476
            self.match(PhiSQLParser.T__1)
            self.state = 477
            self.match(PhiSQLParser.STRING_LITERAL)
            self.state = 482
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4:
                self.state = 478
                self.match(PhiSQLParser.T__3)
                self.state = 479
                self.match(PhiSQLParser.STRING_LITERAL)
                self.state = 484
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 485
            self.match(PhiSQLParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING_LITERAL(self):
            return self.getToken(PhiSQLParser.STRING_LITERAL, 0)

        def NUMERIC_LITERAL(self):
            return self.getToken(PhiSQLParser.NUMERIC_LITERAL, 0)

        def BOOLEAN_LITERAL(self):
            return self.getToken(PhiSQLParser.BOOLEAN_LITERAL, 0)

        def ID(self):
            return self.getToken(PhiSQLParser.ID, 0)

        def getRuleIndex(self):
            return PhiSQLParser.RULE_literal

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteral" ):
                listener.enterLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteral" ):
                listener.exitLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLiteral" ):
                return visitor.visitLiteral(self)
            else:
                return visitor.visitChildren(self)




    def literal(self):

        localctx = PhiSQLParser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 82, self.RULE_literal)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 487
            _la = self._input.LA(1)
            if not(((((_la - 90)) & ~0x3f) == 0 and ((1 << (_la - 90)) & 15) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[23] = self.discoveryPredicate_sempred
        self._predicates[38] = self.predicate_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def discoveryPredicate_sempred(self, localctx:DiscoveryPredicateContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 1)
         

    def predicate_sempred(self, localctx:PredicateContext, predIndex:int):
            if predIndex == 1:
                return self.precpred(self._ctx, 1)
         




