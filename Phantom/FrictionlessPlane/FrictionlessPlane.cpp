/*****************************************************************************

Copyright (c) 2004 SensAble Technologies, Inc. All rights reserved.

OpenHaptics(TM) toolkit. The material embodied in this software and use of
this software is subject to the terms and conditions of the clickthrough
Development License Agreement.

For questions, comments or bug reports, go to forums at: 
    http://dsc.sensable.com

Module Name:

  FrictionlessPlane.cpp

Description: 

  This example demonstrates how to haptically render contact with an infinite
  frictionless plane.  The plane allows popthrough such that if the user 
  applies enough force against the plane, the plane will reverse its sidedness
  and allow the user to interact with it from the opposite side.

*******************************************************************************/
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

HDCallbackCode HDCALLBACK DevicePositionCallback(void *pUserData);
void PrintDevicePosition();


/*******************************************************************************
 Haptic plane callback.  The plane is oriented along Y=0 and provides a 
 repelling force if the device attempts to penetrates through it.
*******************************************************************************/
HDCallbackCode HDCALLBACK FrictionlessPlaneCallback(void *data)
{
    // Stiffnes, i.e. k value, of the plane.  Higher stiffness results
    // in a harder surface.
    const double planeStiffness = .25;

    // Amount of force the user needs to apply in order to pop through
    // the plane.
    const double popthroughForceThreshold = 1000.0;
    
    // Plane direction changes whenever the user applies sufficient
    // force to popthrough it.
    // 1 means the plane is facing +Y.
    // -1 means the plane is facing -Y.
    static int directionFlag = 1;

    hdBeginFrame(hdGetCurrentDevice());

    // Get the position of the device.
    hduVector3Dd position;
    hdGetDoublev(HD_CURRENT_POSITION, position);

    // If the user has penetrated the plane, set the device force to 
    // repel the user in the direction of the surface normal of the plane.
    // Penetration occurs if the plane is facing in +Y and the user's Y position
    // is negative, or vice versa.

    if ((position[1] <= 0 && directionFlag > 0) || 
        (position[1] > 0) && (directionFlag < 0))
    {
        // Create a force vector repelling the user from the plane proportional
        // to the penetration distance, using F=kx where k is the plane 
        // stiffness and x is the penetration vector.  Since the plane is 
        // oriented at the Y=0, the force direction is always either directly 
        // upward or downward, i.e. either (0,1,0) or (0,-1,0).
        double penetrationDistance = fabs(position[1]);
        hduVector3Dd forceDirection(0,directionFlag,0);

        // Hooke's law explicitly:
        double k = planeStiffness;
        hduVector3Dd x = penetrationDistance*forceDirection;
        hduVector3Dd f = k*x;

        // If the user applies sufficient force, pop through the plane
        // by reversing its direction.  Otherwise, apply the repel
        // force.
        if (f.magnitude() > popthroughForceThreshold)
        {
            f.set(0.0,0.0,0.0);
            directionFlag = -directionFlag;
        }

        hdSetDoublev(HD_CURRENT_FORCE, f);
    }

    hdEndFrame(hdGetCurrentDevice());

    // In case of error, terminate the callback.
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
        PrintDevicePosition();
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
    hdGetDoublev(HD_CURRENT_POSITION, pPosition);
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
