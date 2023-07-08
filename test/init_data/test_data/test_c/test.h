#include <stdio.h>
#include <stdlib.h>

int add(int x,int y)
{
    return x+y;
}

int sum(int a,int b)
{
    int c = 0;
    int i = a; 
    for(i=a;i<=b;i++)
    {
        c+=i;
    }
    return c;
}
