#include <bits/stdc++.h>
using namespace std;




int main () {

	ofstream myfile;
	myfile.open ("input.txt");

	long int n = 300;




	long int i,j,k;
	i = j = k = 0;

	float r = 50;

	float r1,r2,r3;


	int range = 20;

	int gap = 5;

	float vel = 1;


	int rmin, rmax;
	rmax = 30;
	rmin = 20;


	vector<int>x_val(n);
	vector<int>y_val(n);

	myfile<<n<<'\n';


	for(int p=0;p<n;p++)
	{

	    r = (rand()%(10*(rmax - rmin)))/10;
	    r = r + rmin;
	    i = (rand()%(20*(int)r) - 10*(int)r) / 10;
	    j = (pow(-1,(p%2)))*sqrt(r*r-i*i);
	    k = 0;

	    x_val[p] = i;
	    y_val[p] = j;

	    myfile<<i<<' '<<j<<' '<<k<<'\n';
	}


	for(int p=0;p<n;p++)
	{

		i = x_val[p];
		j = y_val[p];

		float norm = i*i + j*j;

		norm = sqrt(norm);

				if(norm == 0)
				{
					norm = 1;
				}

	    myfile<<-1*vel*j/norm<<' '<<vel*i/norm<<' '<<'0'<<'\n';
	}


	for(int i=0;i<n;i++)
	{
		myfile<<'3'<<'\n';
	}


	for(int i=0;i<n;i++)
	{
		myfile<<'2'<<'\n';
	}	




	myfile.close();
	return 0;
}
