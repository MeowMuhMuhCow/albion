/************
 * NAME     : TEXTCOMM.C
 * AUTHOR   : Jurie Horneman, BlueByte
 * START    : 8-7-1994
 * PROJECT  : Text functions
 * NOTES    : - These functions assume that NULL and FALSE are 0.
 * SEE ALSO : TEXT.H
 ************/

/*
 ** Pragmas ****************************************************************
 */

#pragma off (unreferenced);

/*
 ** Includes ***************************************************************
 */

#include <string.h>
#include <stdlib.h>

#include <BBDEF.H>
#include <BBMEM.H>

#include <TEXT.H>
#include "TEXTVAR.H"

#include <FONT.H>

/*
 ** Prototypes *************************************************************
 */

UNSHORT Get_LLC_nr(UNCHAR *Text);

/*
 *****************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME      : LLC_handler
 * FUNCTION  : Low level text command handler.
 * FILE      : TEXTCOMM.C
 * AUTHOR    : Jurie Horneman
 * FIRST     : 11.07.94 15:48
 * LAST      : 15.10.95 16:33
 * INPUTS    : UNCHAR *Text - Pointer to string (after command character).
 *             struct LLC_Text_command *Command_list - Pointer to LLC table.
 * RESULT    : UNCHAR * : Pointer to string after command.
 * BUGS      : No known.
 * NOTES     : - All print-function-internal variables that can be changed
 *              by text commands should be implemented as global variables.
 * SEE ALSO  : TEXT.H
 * #FUNCTION HEADER END#
 */

/* #FUNCTION BEGIN# */

UNCHAR *
LLC_handler(UNCHAR *Text, struct LLC_Text_command *Command_list)
{
	BOOLEAN Found_command_flag;
	BOOLEAN Failure;
	UNSHORT i;
	UNCHAR Command[4];
	UNCHAR Char;

	/* Try to read text command */
	Failure = FALSE;
	for (i=0;i<4;i++)
	{
		/* Get character */
		Char = *Text++;

		/* Is premature end of command ? */
		if (Char == COMEND_CHAR)
		{
			/* Yes -> Report error */
			Text_error(TEXTERR_COMMAND_TOO_SHORT);

			/* Abort */
			Failure = TRUE;
			break;
		}
		else
		{
			/* No -> Store character */
			Command[i] = Char;
		}
	}

	/* Failure ? */
	if (Failure)
	{
		/* Yes -> Skip command */
		return Text;
	}

	/* Is BLOK command ? */
	if ((Command[0] == 'B') &&
	 (Command[1] == 'L') &&
	 (Command[2] == 'O') &&
	 (Command[3] == 'K'))
	{
		/* Yes -> Search end of text */
		while (*Text)
			Text++;

		/* Exit */
		return Text;
	}

	/* Search text command in command list */
	while (Command_list->Command_handler)
	{
		/* Compare commands */
		Found_command_flag = TRUE;
		for (i=0;i<4;i++)
		{
			if (Command_list->Command[i] != Command[i])
			{
				Found_command_flag = FALSE;
				break;
			}
		}

		/* Found ? */
		if (Found_command_flag)
		{
			/* Yes -> Execute */
			(Command_list->Command_handler)(Text);
			break;
		}

		/* No -> Next command */
		Command_list++;
	}

	/* Seek end of command */
	Char = *Text++;
	while (Char != COMEND_CHAR)
		Char = *Text++;

	return Text;
}

/*
 *****************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME      : Get_LLC_nr
 * FUNCTION  : Get 3-digit number from text command.
 * FILE      : TEXTCOMM.C
 * AUTHOR    : Jurie Horneman
 * FIRST     : 12.07.94 14:08
 * LAST      : 12.07.94 14:08
 * INPUTS    : UNCHAR *Text - Pointer to string (after command).
 * RESULT    : UNSHORT : Number.
 * BUGS      : No known.
 * SEE ALSO  : TEXT.H
 * #FUNCTION HEADER END#
 */

/* #FUNCTION BEGIN# */

UNSHORT
Get_LLC_nr(UNCHAR *Text)
{
	UNCHAR Number[] = "000";

	strncpy(Number,Text,3);
	return((UNSHORT) strtoul(Number, NULL, 10));
}

/*
 *****************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME      : LLC_ ...
 * FUNCTION  : Low level text commands.
 * FILE      : TEXTCOMM.C
 * AUTHOR    : Jurie Horneman
 * FIRST     : 12.07.94 14:04
 * LAST      : 23.08.94 12:17
 * INPUTS    : UNCHAR *Text - Pointer to string (after command).
 * RESULT    : None.
 * BUGS      : No known.
 * SEE ALSO  : TEXT.H
 * #FUNCTION HEADER END#
 */

/* #FUNCTION BEGIN# */

void
LLC_Set_ink(UNCHAR *Text)
{
	Current_text_style.Ink = Get_LLC_nr(Text);
}
/* LLC_Set_shadow: text command - set the shadow colour */
void
LLC_Set_shadow(UNCHAR *Text)
{
	Current_text_style.Shadow = Get_LLC_nr(Text);
}
/* LLC_No_shadow: text command - switch the shadow off */
void
LLC_No_shadow(UNCHAR *Text)
{
	Current_text_style.Shadow = 0xFFFF;
}
/* LLC_Set_normal_style: text command - normal text style */
void
LLC_Set_normal_style(UNCHAR *Text)
{
	Current_text_style.Style = NORMAL_STYLE;
}
/* LLC_Set_fat_style: text command - fat text style */
void
LLC_Set_fat_style(UNCHAR *Text)
{
	Current_text_style.Style = FAT_STYLE;
}
/* LLC_Set_high_style: text command - high text style */
void
LLC_Set_high_style(UNCHAR *Text)
{
	Current_text_style.Style = HIGH_STYLE;
}
/* LLC_Set_fat_high_style: text command - fat and high text style */
void
LLC_Set_fat_high_style(UNCHAR *Text)
{
	Current_text_style.Style = FAT_HIGH_STYLE;
}
/* LLC_Set_big_style: text command - big text style */
void
LLC_Set_big_style(UNCHAR *Text)
{
	Current_text_style.Style = BIG_STYLE;
}
/* LLC_Set_normal_font: text command - normal font */
void
LLC_Set_normal_font(UNCHAR *Text)
{
	Current_text_style.Font = &Normal_font;
}
/* LLC_Set_techno_font: text command - techno font */
void
LLC_Set_techno_font(UNCHAR *Text)
{
	Current_text_style.Font = &Techno_font;
}
/* LLC_Set_capital: text command - start a coloured capital letter */
void
LLC_Set_capital(UNCHAR *Text)
{
	Current_text_style.Style = FAT_HIGH_STYLE;
	Current_text_style.Ink = CAPITAL_COLOUR;
	TEXT_Current_X += 16;
	Width_without_spaces += 16;
}
/* LLC_Unset_capital: text command - end the capital letter */
void
LLC_Unset_capital(UNCHAR *Text)
{
	Current_text_style.Style = NORMAL_STYLE;
	Current_text_style.Ink = Textstyle_stack[Textstyle_stack_index]->Ink;
}
/* LLC_Default: text command - back to the default text style */
void
LLC_Default(UNCHAR *Text)
{
	Current_text_style.Font = &Normal_font;
	Current_text_style.Style = NORMAL_STYLE;
	Current_text_style.Ink = Textstyle_stack[Textstyle_stack_index]->Ink;
	Current_text_style.Shadow = Textstyle_stack[Textstyle_stack_index]->Shadow;
	Current_text_style.Justification = PRINT_JUSTIFIED;
}
/* LLC_HJump: text command - move the cursor to the right */
void
LLC_HJump(UNCHAR *Text)
{
	UNSHORT dX;

	dX = Get_LLC_nr(Text);

	TEXT_Current_X += dX;
	Width_without_spaces += dX;
}
/* LLC_VJump: text command - increase the line spacing */
void
LLC_VJump(UNCHAR *Text)
{
	UNSHORT dY;

	dY = Get_LLC_nr(Text);

	if (dY > Current_line_info.Skip)
		Current_line_info.Skip = dY;
}
/* LLC_Set_centered: text command - centred text */
void
LLC_Set_centered(UNCHAR *Text)
{
	Current_text_style.Justification = PRINT_CENTERED;
}
/* LLC_Set_left: text command - left-aligned text */
void
LLC_Set_left(UNCHAR *Text)
{
	Current_text_style.Justification = PRINT_LEFT;
}
/* LLC_Set_right: text command - right-aligned text */
void
LLC_Set_right(UNCHAR *Text)
{
	Current_text_style.Justification = PRINT_RIGHT;
}
/* LLC_Set_justified: text command - justified text */
void
LLC_Set_justified(UNCHAR *Text)
{
	Current_text_style.Justification = PRINT_JUSTIFIED;
}

