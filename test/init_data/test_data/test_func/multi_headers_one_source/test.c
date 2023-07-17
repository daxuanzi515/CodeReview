#include "test.h"
#include "gg.h"
int sum(int a,int b)
{
    int i;
    int c = 0;
    for(i=a; i<=b; i++)
        c += i;
    return c;
}
void func()
{
    printf("%d\n",1001);
}
void test(int x)
{
    x += 100;
    printf("%d\n",x);
}
int main()
{
    int res = sum(-1,10);
    func();
    test(100);
    printf("res: %d\n", res);
    return 0;
}