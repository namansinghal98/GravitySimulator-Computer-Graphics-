#include <bits/stdc++.h>
using namespace std;




int main () {

	ofstream myfile;
	myfile.open ("input.txt");

	long int n = 0;


	long int i,j,k;
	i = j = k = 0;

	float r = 50;

	float r1,r2,r3;


	int range = 200;

	int gap = 4;

	float vel = 25;


	for(long int i=-range;i<=range;i+=gap)
	{
		for(long int j=-range;j<=range;j+=gap)
		{
				n++;
		}
	}

	myfile<<n<<'\n';


	for(long int i=-range;i<=range;i+=gap)
	{
		for(long int j=-range;j<=range;j+=gap)
		{
	    		myfile<<i<<' '<<j<<' '<<' '<<'0'<<'\n';
		}
	}


	for(long int i=-range;i<=range;i+=gap)
	{
		for(long int j=-range;j<=range;j+=gap)
		{
				float norm = i*i + j*j;
				norm = sqrt(norm);

				if(norm == 0)
				{
					norm = 1;
				}


	    		myfile<<vel*i/norm<<' '<<vel*j/norm<<' '<<vel*k/norm<<'\n';
	    		// myfile<<i<<' '<<j<<' '<<' '<<'\n';

		}
	}


	for(long int i=-range;i<=range;i+=gap)
	{
		for(long int j=-range;j<=range;j+=gap)
		{
			
				// if(i == j && j == 0)
				// 	myfile<<"20"<<'\n';					
				// else
					myfile<<'2'<<'\n';
		}
	}



	for(long int i=-range;i<=range;i+=gap)
	{
		for(long int j=-range;j<=range;j+=gap)
		{

				// if(i == j && j == 0)
				// 	myfile<<'5'<<'\n';					
				// else
					myfile<<'1'<<'\n';
		}
	}

	myfile.close();
	return 0;
}
