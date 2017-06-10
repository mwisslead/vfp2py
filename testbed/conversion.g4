parser grammar conversion;
options { tokenVocab=conversionLexer; }

conversionTests: conversionTest*;

conversionTest: FoxStart FoxLine* FoxEnd PyStart PyLine* PyEnd;
