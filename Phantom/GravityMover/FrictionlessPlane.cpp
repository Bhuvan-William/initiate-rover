#ifdef  _WIN64
#pragma warning (disable:4996)
#endif

#include <cstdio>
#include <cassert>
#include <stdlib.h>
#include <string.h>

#if defined(WIN32)
# include <conio.h>
#else
# include "conio.h"
#endif

#include <HD/hd.h>
#include <HDU/hduVector.h>
#include <HDU/hduError.h>

#define MAX_INPUT_DOF   6   
#define MAX_OUTPUT_DOF  6

#define BUZZ_SIZE 1024

#define MOVESPEED 2000
#define YMOVESPEED 6000

#define MAX_STRING 1024
#define ERROR 0.01


HDCallbackCode HDCALLBACK DevicePositionCallback(void *pUserData);
void PrintDevicePosition();
void delete_at(char *src, int pos, int len);

static long motors[MAX_OUTPUT_DOF];

float tox = -0.5;
float toy = 1;
float toz = 1;

float oldtox;
float oldtoy;
float oldtoz;

/*
float a = 0.025;
float b = 0.8;
float c = 6.66;	
*/

float a = 0.025;
float b = 1.332;
float c = 0.235;

int instruction = 1;


bool stabilised = false;


hduVector3Dd wellPos;


HDCallbackCode HDCALLBACK FrictionlessPlaneCallback(void *data)
{


	hdBeginFrame(hdGetCurrentDevice());


	char buff[BUZZ_SIZE];
	FILE *f = fopen("/home/robot/Documents/yeet.txt", "r");
	fgets(buff, BUZZ_SIZE, f);
	fclose(f);
	
	char toxs[BUZZ_SIZE];
	memcpy(toxs, &buff[0], 8);
	char toys[BUZZ_SIZE];
	memcpy(toys, &buff[9], 8);
	char tozs[BUZZ_SIZE];
	memcpy(tozs, &buff[18], 8);

	

	if (toxs[0] == '+') {
		delete_at(toxs, 0, 0);
	}
	if (toys[0] == '+') {
		delete_at(toys, 0, 0);
	}
	if (tozs[0] == '+') {
		delete_at(tozs, 0, 0);
	}


	tox = atof(toxs);
	toy = atof(toys);
	toz = atof(tozs);

	if (oldtox != tox || oldtoy != toy || oldtoz != toz) {
		instruction += 1;
	}
	

	wellPos = {tox, toy, toz};

	

	
	hduVector3Dd position;
	hduVector3Dd force;
	hduVector3Dd positionTwell;

	hdGetDoublev(HD_CURRENT_POSITION, position);
	
	memset(force, 0, sizeof(hduVector3Dd));
	
	hduVecSubtract(positionTwell, wellPos, position);

	//const HDdouble kStiffness = 0.025;
	//const HDdouble kStiffness = 0.5;
	const HDdouble kGravityWellInfluence = 20000;

	float total = sqrt(pow(positionTwell[0], 2)+pow(positionTwell[1], 2)+pow(positionTwell[2], 2));
	
	//const HDdouble kStiffness = a + b/(pow(2, (total/c)));
	HDdouble kStiffness;
	
	
	if (total < 7 || instruction < 5) {
		kStiffness = 0.5;
	}
	else {
		kStiffness = 0.025;
	}

	if (hduVecMagnitude(positionTwell) < kGravityWellInfluence)
	{
	    hduVecScale(force, positionTwell, kStiffness);
	}

	
	
	
	//fprintf(stderr, "%f   %f\n", kStiffness, total);
	

	hdSetDoublev(HD_CURRENT_FORCE, force);
	//fprintf(stderr, "should be at x%f y%f z%f, at x%f y%f z%f\n", tox, toy, toz, position[0], position[1], position[2]);
	
	oldtox = tox;
	oldtoy = toy;
	oldtoz = toz;


	hdEndFrame(hdGetCurrentDevice());

    HDErrorInfo error;
    if (HD_DEVICE_ERROR(error = hdGetError()))
    {
        hduPrintError(stderr, &error, "Error detected during main scheduler callback\n");

        if (hduIsSchedulerError(&error))
        {
            return HD_CALLBACK_DONE;  
        }
    }

    return HD_CALLBACK_CONTINUE;
}


int main(int argc, char* argv[])
{
    HDErrorInfo error;
    HHD hHD = hdInitDevice("Touch me");

    hdEnable(HD_FORCE_OUTPUT);
    hdStartScheduler();

    HDCallbackCode hPlaneCallback = hdScheduleAsynchronous(
        FrictionlessPlaneCallback, 0, HD_DEFAULT_SCHEDULER_PRIORITY);


    while (HD_TRUE)
    {       
        //PrintDevicePosition();
    }

    hdStopScheduler();
    hdUnschedule(hPlaneCallback);
    hdDisableDevice(hHD);

    return 0;
}


HDCallbackCode HDCALLBACK DevicePositionCallback(void *pUserData)
{
    HDdouble *pPosition = (HDdouble *) pUserData;

    //hdBeginFrame(hdGetCurrentDevice());
    hdGetDoublev(HD_CURRENT_JOINT_ANGLES, pPosition);
    //hdEndFrame(hdGetCurrentDevice());

    return HD_CALLBACK_DONE;
}






void delete_at(char *src, int pos, int len)
	{
		char *dst;
		int i;
		if ( pos < 0 )
		    return;

		if ( len <= 0 )
		    len = MAX_STRING;
		if ( pos >= len )
		    return;
		src += pos;
		dst = src;
		src++;
		for ( i = pos + 1; i < len && *src != 0; i++ )
		    *dst++ = *src++;

		*dst = 0;
		return;
	}
