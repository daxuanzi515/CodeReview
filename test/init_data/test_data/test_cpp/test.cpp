#include "test.h"
#include "test_headers.h"
int hub(int a, int b)
{
    return (a-b);
}
int add(int a,int b)
{
    return a+b;
}
void xxx(int bye)
{
    int b = bye;
	printf("xxx: %d\n", b);
}
void sum()
{
    printf("Sadness\n");
}
bool temp(int a)
{
	if(a<100)
		return false;
	else
		return true;
}
void kkk(int a)
{
    a = 2;
}
int test(int i)
{
	return 100;
}