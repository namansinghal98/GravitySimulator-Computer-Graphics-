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

	int range = 60;

	int gap = 5;

	float vel = 200;


	for(long int i=-range;i<range;i+=gap)
	{
		for(long int j=-range;j<range;j+=gap)
		{
			for(long int k=-range;k<range;k+=gap)
			{

				n++;
			}
		}
	}

	myfile<<n<<'\n';


	for(long int i=-range;i<range;i+=gap)
	{
		for(long int j=-range;j<range;j+=gap)
		{
			for(long int k=-range;k<range;k+=gap)
			{

	    		myfile<<i<<' '<<j<<' '<<k<<'\n';
			}
		}
	}


	for(long int i=-range;i<range;i+=gap)
	{
		for(long int j=-range;j<range;j+=gap)
		{
			for(long int k=-range;k<range;k+=gap)
			{

				float norm = i*i + j*j + k*k;
				norm = sqrt(norm);

				if(norm == 0)
				{
					norm = 1;
				}


	    		myfile<<vel*i/norm<<' '<<vel*j/norm<<' '<<vel*k/norm<<'\n';
			}
		}
	}


	for(long int i=-range;i<range;i+=gap)
	{
		for(long int j=-range;j<range;j+=gap)
		{
			for(long int k=-range;k<range;k+=gap)
			{
				myfile<<'3'<<'\n';
			}
		}
	}



	for(long int i=-range;i<range;i+=gap)
	{
		for(long int j=-range;j<range;j+=gap)
		{
			for(long int k=-range;k<range;k+=gap)
			{

				myfile<<"1"<<'\n';
			}
		}
	}

	myfile.close();
	return 0;
}
