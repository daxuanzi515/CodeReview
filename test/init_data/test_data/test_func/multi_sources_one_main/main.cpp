#include "one.h"
#include "two.h"
int main()
{
    int res1 = add(100, 101);
    int res2 = sub(101, 100);
    printf("res1: %d\n",res1);
    printf("res2: %d\n",res2);
    int res3 = res1 + res2;
    func(res3);
	int res4 = sum(-1,10);
    func(res4);
	return 0;
}