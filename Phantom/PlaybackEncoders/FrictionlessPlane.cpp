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

bool stabilised = false;

HDCallbackCode HDCALLBACK FrictionlessPlaneCallback(void *data)
{
	motors[0] = 0;
	motors[1] = 0;
	motors[2] = 0;

	hdBeginFrame(hdGetCurrentDevice());

	hduVector3Dd angles;

	char buff[BUZZ_SIZE];
	FILE *f = fopen("/home/robot/Documents/yeet.txt", "r");
	fgets(buff, BUZZ_SIZE, f);
	fclose(f);
	
	char toxs[BUZZ_SIZE];
	memcpy(toxs, &buff[0], 6);
	char toys[BUZZ_SIZE];
	memcpy(toys, &buff[7], 6);
	char tozs[BUZZ_SIZE];
	memcpy(tozs, &buff[14], 6);

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
	
	//toy = (fabs(toy)/toy)*(fabs(toy)+0.025);
	//toz = (fabs(toz)/toz)*(fabs(toz)+0.025);

	//toy = toy - 0.1;
	



    hdGetDoublev(HD_CURRENT_JOINT_ANGLES, angles);
	


	if (tox > angles[0] + ERROR) {
		motors[0] = MOVESPEED;	
	}
	else if (tox < angles[0] - ERROR) {
		motors[0] = -MOVESPEED;
	}
	
	if (toy > angles[1] + ERROR) {
		motors[1] = YMOVESPEED;	
	}
	else if (toy < angles[1] - ERROR) {
		motors[1] = -YMOVESPEED;
	}

	if (toz > angles[2] + ERROR) {
		motors[2] = YMOVESPEED;	
	}
	else if (toz < angles[2] - ERROR) {
		motors[2] = -YMOVESPEED;
	}



	if (oldtox != tox || oldtoy != toy || oldtoz != toz) {
		stabilised = false;
	}




	
	/*if (tox > angles[0]-ERROR && tox < angles[0]+ERROR && toy < angles[1]+ERROR && toy > angles[1]-ERROR && toz < angles[2]+ERROR && toz > angles[2]-ERROR || stabilised == true){

	    hduVector3Dd f;
		f.set(0, 1, 0);
		
		
		if (tox > angles[0] - ERROR) {
			f[0] = -1;
			//printf("moving left\n");
		}	
		else if (tox < angles[0] + ERROR) {
			f[0] = 1;
			//printf("moving right\n");
		}

		if (toy > angles[1] - ERROR && toz > angles[2] - ERROR) {
			printf("Stablilsing down\n");
			f[1] = 1;

		}	
		else if (toy < angles[1] + ERROR && toz < angles[2] + ERROR) {
			printf("Stablilsing up\n");
			f[1] = -1;
		}
		else {
			stabilised = false;
		}

		

		hdSetDoublev(HD_CURRENT_FORCE, f);
		fprintf(stderr, "stabilising");
		stabilised = true;
	}
	else {
		printf("Motors set to %i %i %i\n", motors[0], motors[1], motors[2]);
		hdSetLongv(HD_CURRENT_MOTOR_DAC_VALUES, motors);


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
	printf("Encoders %f %f %f\n", angles[0], angles[1], angles[2]);


	//fprintf(stderr, "%f#%f#%f", motors[0], motors[1], motors[2]);
	*/	
	if (tox > angles[0]-ERROR && tox < angles[0]+ERROR && toy < angles[1]+ERROR && toy > angles[1]-ERROR && toz < angles[2]+ERROR && toz > angles[2]-ERROR){
					
		
	}
	else {
				
		fprintf(stderr, "moving");
	}
	
	hdSetLongv(HD_CURRENT_MOTOR_DAC_VALUES, motors);
	


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


void PrintDevicePosition()
{
    hduVector3Dd position;

    hdScheduleSynchronous(DevicePositionCallback, position,
        HD_DEFAULT_SCHEDULER_PRIORITY);


    HDint nCurrentButtons;
    hdGetIntegerv(HD_CURRENT_BUTTONS, &nCurrentButtons);

    printf("x%.3f:y%.3f:z%.3f:", 
        position[0], position[1], position[2]);

    int b1;
    int b2;


    if ((nCurrentButtons & HD_DEVICE_BUTTON_1) != 0)
    {
        /* Detected button down */
	printf("1:");
	b1 = 1;
    }
    else if ((nCurrentButtons & HD_DEVICE_BUTTON_1) == 0)

    {
        /* Detected button up */
        printf("0:");
	b1 = 0;
    }


    if ((nCurrentButtons & HD_DEVICE_BUTTON_2) != 0)
    {
        /* Detected button down */
	printf("1");
	b2 = 1;
    }
    else if ((nCurrentButtons & HD_DEVICE_BUTTON_2) == 0)

    {
        /* Detected button up */
        printf("0");
	b2 = 0;
    }

    printf("\n");

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
