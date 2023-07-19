#include "test.h"
void func()
{
    printf("This is the first function.\n");
}
int main()
{
	int a;
	scanf("%d",&a);
    int res = multi(2, 4);
    test(res);
    print();
}