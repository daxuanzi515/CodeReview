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
	int res1 = add(200,199);
	int res2 = sub(200, 199);
	int res3 = res1-res2;
	printf("add(200,199)-sub(199,200):%d\n",res3);
    return 0;
}