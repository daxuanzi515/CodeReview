#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gg.h"
#include "test.h"
void invalidFunction() {
}
void unusedVariableExample() {
    int unusedVar;
}
void dangerousFunction(const char* input) {
    char buffer[10];
    strcpy(buffer, input);
}
void memoryLeakExample() {
    char* dynamicString = (char*)malloc(20 * sizeof(char));
}
void free_()
{
	int* pointer = (int*)malloc(sizeof(int));
	free(pointer);
	free(pointer);
}
int main() {
    unusedVariableExample();
    char userInput[1];
    printf("input a word please:\n");
    scanf("%s", userInput);
    printf("yourInput: %s\n",userInput);
    dangerousFunction(userInput);
    memoryLeakExample();
	
	int RES1 = add(200,199);
	int RES2 = sub(200, 199);
	int RES3 = RES1-RES2;
	printf("add(200,199)-sub(199,200):%d\n",RES3);
    return 0;
}