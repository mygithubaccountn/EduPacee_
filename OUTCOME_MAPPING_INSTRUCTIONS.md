# How to Create the Outcome Mapping Graph

The Outcome Mapping Graph visualizes the connections between:
- **Assessments** (green diamonds) → **Learning Outcomes** (purple boxes) → **Program Outcomes** (blue boxes)

## Prerequisites
1. A course must exist (created by Academic Board)
2. Students must be enrolled in the course
3. A teacher must be assigned to the course

## Step-by-Step Instructions

### Step 1: Academic Board - Create Program Outcomes
1. Log in as **Academic Board**
2. Go to Dashboard
3. Click **"Add Program Outcome"** (or go to `/academic-board/add-program-outcome/`)
4. Enter:
   - **Code**: e.g., `PO1`, `PO2`, `PO3`
   - **Description**: e.g., "Students will demonstrate problem-solving skills"
5. Click **"Add Program Outcome"**
6. Repeat to create multiple Program Outcomes (PO1, PO2, etc.)

### Step 2: Teacher - Create Learning Outcomes
1. Log in as **Teacher**
2. Go to Dashboard
3. Click on a course you teach
4. In the **"Learning Outcomes"** section, click **"Add"**
5. Enter:
   - **Code**: e.g., `LO1`, `LO2`, `LO3`
   - **Description**: e.g., "Students can write Python programs"
6. Click **"Add Learning Outcome"**
7. Repeat to create multiple Learning Outcomes

### Step 3: Teacher - Create Assessments
1. While viewing the course (as Teacher)
2. In the **"Assessments"** section, click **"Add"**
3. Enter:
   - **Name**: e.g., `Midterm`, `Project`, `Final`, `Quiz`
   - **Weight in Course**: e.g., `0.4` (for 40%), `0.3` (for 30%)
4. Click **"Add Assessment"**
5. Repeat to create multiple assessments

### Step 4: Teacher - Connect Assessments to Learning Outcomes
1. While viewing the course (as Teacher)
2. In the **"Connections"** section, click **"Connect"**
3. Select:
   - **Assessment**: e.g., "Midterm"
   - **Learning Outcome**: e.g., "LO1"
   - **Weight**: e.g., `0.6` (this means Midterm contributes 60% to LO1's score)
4. Click **"Create Connection"**
5. Repeat to connect multiple assessments to learning outcomes
   - Example: Midterm (0.6) and Project (0.4) both connect to LO1

### Step 5: Academic Board - Connect Learning Outcomes to Program Outcomes
1. Log in as **Academic Board**
2. Go to the course detail page
3. In the **"Learning Outcome to Program Outcome Connections"** section, click **"Connect"**
4. Select:
   - **Learning Outcome**: e.g., "LO1"
   - **Program Outcome**: e.g., "PO1"
   - **Weight**: e.g., `1.0` (this means LO1 contributes fully to PO1)
5. Click **"Create Connection"**
6. Repeat to connect multiple learning outcomes to program outcomes

### Step 6: View the Graph
The graph will automatically appear on:
- **Teacher View**: Course detail page (shows structure)
- **Academic Board View**: Course detail page (shows structure)
- **Student View**: Course detail page (shows structure + their scores)

## Graph Elements

- **Green Diamonds** = Assessments (Midterm, Project, Final, etc.)
- **Purple Boxes** = Learning Outcomes (LO1, LO2, etc.)
- **Blue Boxes** = Program Outcomes (PO1, PO2, etc.)
- **Edges with percentages** = Connections showing weights (e.g., "40%", "60%")

## Example Workflow

1. **Academic Board** creates:
   - PO1: "Problem Solving"
   - PO2: "Communication Skills"

2. **Teacher** creates for Course CS101:
   - LO1: "Write Python programs"
   - LO2: "Debug code"
   - Assessment: "Midterm" (weight: 0.4)
   - Assessment: "Project" (weight: 0.6)

3. **Teacher** connects:
   - Midterm → LO1 (weight: 0.6)
   - Project → LO1 (weight: 0.4)
   - Midterm → LO2 (weight: 0.5)
   - Project → LO2 (weight: 0.5)

4. **Academic Board** connects:
   - LO1 → PO1 (weight: 1.0)
   - LO2 → PO1 (weight: 0.5)
   - LO2 → PO2 (weight: 0.5)

5. **Result**: Graph shows the complete flow from Assessments → LOs → POs!

## Troubleshooting

**Graph is empty?**
- Make sure you have at least:
  - 1 Assessment
  - 1 Learning Outcome
  - 1 Connection between Assessment and Learning Outcome
- The graph needs at least one connection to display

**No Program Outcomes showing?**
- Program Outcomes only appear if they're connected to Learning Outcomes
- Make sure Academic Board has created LO → PO connections

**Student scores not showing?**
- Students need to have Assessment Grades entered
- Teacher must enter grades via "Add Assessment Grade"

