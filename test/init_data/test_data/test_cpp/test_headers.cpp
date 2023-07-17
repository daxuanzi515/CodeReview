#include "test.h"
#include "test_headers.h"
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
int main()
{
    int res = add(1,2);
    sum();
	int a;
	scanf("%d",&a);
	printf("a: %d\n", a);
    kkk(123);
    printf("res: %d\n", res);
    sum();
	bool fLAG = temp(100);
	printf("flag: %d\n", fLAG);
    xxx(1223);
    int res1 = hub(5,1);
    printf("res1: %d\n", res1);
    return 0;
}
