#include "test_headers.h"
#include "test.h"
void sum();

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
    kkk(123);
    printf("res: %d\n", res);
    sum();
	bool flag = temp(100);
	printf("flag: %d\n", flag);
    xxx(1223);
//    int res1 = sub(5,0);
//    printf("res1: %d\n", res1);
//    fun();
    return 0;
}
