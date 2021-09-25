from asyncio.windows_events import NULL
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image

from SubmissionClass import *
from CodeforceClass import *
from FilterClass import *
from RandomClass import *

import discord, asyncio, random, os
import datetime as dt

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='$')

LOWERCASE_CODEFORCE_CODES = list('abcdefghi')
UPPERCASE_CODEFORCE_CODES = list('ABCDEFGHI')



class WrongProblemInput(Exception):
    """Raised when inputted codeforce problem code has unusual lettering"""
    pass



@bot.event
async def on_ready() -> None:
    print(f'{bot.user} connected')



@bot.command(name="cf", pass_context=True, help='sends codeforce problem with problem code requested, ex. 1540A, 1431E')
async def cf(ctx, problem: str):
    """user types a codeforce problem code, function crops and sends back"""

    try:
        T = CodeforceProblem(problem)
        for picture in T.crop_codeforce_problem():
            await ctx.send(file=discord.File(picture))

    except IndexError:
        # check if any letters from a-f or A-F inclusive
        if [item 
            for item in problem 
            if item in LOWERCASE_CODEFORCE_CODES + UPPERCASE_CODEFORCE_CODES] == []:
            
            await ctx.send("```Problem does not exist```")
        
        elif [item for item in problem if item in UPPERCASE_CODEFORCE_CODES] != []:
            await ctx.send('```Problem doesn\'t exist```')

        else:
            await ctx.send('```Use capital letter(s)```')

    except:
        await ctx.send('```Problem does not exist```')



@bot.command(name='random', help='sends random codeforce problem')
async def rand(ctx: Any) -> None:
    """user types 'random' and function finds it, crops and sends it back"""

    try:
        T = RandomProblem("https://codeforces.com/problemset")
        
        temp = T.give_problem()

        E = CodeforceProblem(temp)
        M = SubmitProblem(temp)
        
        await ctx.send(f'```Submit at: {M.send_submit_link()}```')
        for picture in E.crop_codeforce_problem():
            await ctx.send(file=discord.File(picture))

    except:
        """in case codeforces bugs out, try again"""

        T = RandomProblem("https://codeforces.com/problemset")
        temp = T.give_problem()
        E = CodeforceProblem(temp)
        M = SubmitProblem(temp)
        await ctx.send(f'```Submit at: {M.send_submit_link()}```')
        for picture in E.crop_codeforce_problem():
            await ctx.send(file=discord.File(picture))



@bot.command(name='filter', help='sends random codeforce problem fitting given requirements')
async def filter(ctx: Any, min_rating: int, max_rating: int, *tags: tuple) -> None:
    """filters problems using sent requests"""

    try:
        T = FilterProblem(min_rating, max_rating, *tags)
        E = RandomProblem(T.build_link())
        
        temp = E.give_problem()

        M = CodeforceProblem(temp)
        P = SubmitProblem(temp)

        await ctx.send(f"```Submit at: {P.send_submit_link()}```")
        for picture in M.crop_codeforce_problem():
            await ctx.send(file=discord.File(picture))
    
    except:
        await ctx.send("```No problems within filter```")



@bot.command(name='submit', help='links to codeforce page with submission space highlighted')
async def submit(ctx, problem: str) -> None:
    """function to submit a problem at the link"""
    try:
        T = SubmitProblem(problem)
        
        await ctx.send(T.send_submit_link())

    except IndexError:
        all_found_codes = [item for item in problem 
                           if item in LOWERCASE_CODEFORCE_CODES + UPPERCASE_CODEFORCE_CODES]

        # check if any letters from a-f or A-F inclusive
        if all_found_codes == []:
            await ctx.send("```Problem does not exist```")
        
        elif [item for item in problem if item in UPPERCASE_CODEFORCE_CODES] != []:
            await ctx.send('```Problem doesn\'t exist```')

        else:
            await ctx.send('```Use capital letter(s)```')

    except:
        await ctx.send('```Problem does not exist```')



bot.run(TOKEN)
